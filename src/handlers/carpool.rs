/// Carpool Tracker – Issue #16
///
/// Allows paid event participants to offer rides to other participants.
/// Drivers post their origin city/state, available seats, and contact email.
/// Riders can claim a seat; once full the offer is closed.
use axum::{
    extract::{Form, Path, State},
    response::{IntoResponse, Redirect, Response},
};
use serde::Deserialize;
use tower_sessions::Session;

use crate::{
    auth::{get_current_user, get_or_create_csrf_token, validate_csrf},
    error::{render, AppError},
    models::{CarpoolOffer, CarpoolOfferListRow, CarpoolRiderRow, Event, Participant},
    state::AppState,
};
use crate::handlers::pages::build_base_ctx;

// ── List all offers for the active event ─────────────────────────────────────

pub async fn index(
    State(state): State<AppState>,
    session: Session,
) -> Result<impl IntoResponse, AppError> {
    let event = sqlx::query_as::<_, Event>("SELECT * FROM events WHERE is_active = 1 LIMIT 1")
        .fetch_optional(&state.db)
        .await?;

    let offers: Vec<CarpoolOfferListRow> = if let Some(ref e) = event {
        sqlx::query_as::<_, CarpoolOfferListRow>(r#"
            SELECT co.id,
                   co.driver_id,
                   co.event_id,
                   co.origin_city,
                   co.origin_state,
                   co.total_seats,
                   co.notes,
                   co.contact_email,
                   co.created_time,
                   u.username   AS driver_username,
                   CAST(COALESCE(COUNT(cr.id), 0) AS INTEGER) AS "rider_count: i64"
              FROM carpool_offers co
              JOIN participants  p  ON p.id  = co.driver_id
              JOIN users         u  ON u.id  = p.user_id
              LEFT JOIN carpool_riders cr ON cr.offer_id = co.id
             WHERE co.event_id = ?
             GROUP BY co.id
             ORDER BY co.origin_state, co.origin_city
            "#)
        .bind(e.id)
        .fetch_all(&state.db)
        .await?
    } else {
        Vec::new()
    };

    let user = get_current_user(&session, &state.db).await;
    let participant_id: Option<i64> = if let (Some(u), Some(ref e)) = (&user, &event) {
        sqlx::query_scalar::<_, i64>("SELECT id FROM participants WHERE user_id = ? AND event_id = ?")
        .bind(u.id)
        .bind(e.id)
        .fetch_optional(&state.db)
        .await?
    } else {
        None
    };

    let csrf = get_or_create_csrf_token(&session).await;
    let mut ctx = build_base_ctx(&state, &session).await;
    ctx.insert("event", &event);
    ctx.insert("offers", &offers);
    ctx.insert("participant_id", &participant_id);
    ctx.insert("csrf_token", &csrf);
    render(&state.tera, "carpool/index.html", &ctx)
}

// ── Offer detail ──────────────────────────────────────────────────────────────

pub async fn offer_detail(
    State(state): State<AppState>,
    session: Session,
    Path(offer_id): Path<i64>,
) -> Result<impl IntoResponse, AppError> {
    let offer = sqlx::query_as::<_, CarpoolOffer>("SELECT * FROM carpool_offers WHERE id = ?")
        .bind(offer_id)
        .fetch_optional(&state.db)
        .await?
        .ok_or(AppError::NotFound)?;

    let event = sqlx::query_as::<_, Event>("SELECT * FROM events WHERE id = ?")
        .bind(offer.event_id)
        .fetch_optional(&state.db)
        .await?
        .ok_or(AppError::NotFound)?;

    let driver_username: String = sqlx::query_scalar::<_, String>("SELECT u.username FROM participants p JOIN users u ON u.id = p.user_id WHERE p.id = ?")
        .bind(offer.driver_id)
    .fetch_one(&state.db)
    .await
        .unwrap_or_default();

    let riders = sqlx::query_as::<_, CarpoolRiderRow>(r#"
        SELECT u.username, cr.joined_time
          FROM carpool_riders cr
          JOIN participants   p  ON p.id  = cr.rider_id
          JOIN users          u  ON u.id  = p.user_id
         WHERE cr.offer_id = ?
         ORDER BY cr.joined_time
        "#)
        .bind(offer_id)
    .fetch_all(&state.db)
    .await?;

    let rider_count = riders.len() as i64;
    let seats_remaining = offer.total_seats - rider_count;
    let is_full = seats_remaining <= 0;

    let user = get_current_user(&session, &state.db).await;
    let participant = if let Some(u) = &user {
        sqlx::query_as::<_, Participant>("SELECT * FROM participants WHERE user_id = ? AND event_id = ?")
        .bind(u.id)
        .bind(offer.event_id)
        .fetch_optional(&state.db)
        .await?
    } else {
        None
    };

    let is_driver = participant
        .as_ref()
        .map(|p| p.id == offer.driver_id)
        .unwrap_or(false);

    let is_rider = if let Some(ref p) = participant {
        sqlx::query_scalar::<_, i64>("SELECT COUNT(*) FROM carpool_riders WHERE offer_id = ? AND rider_id = ?")
        .bind(offer_id)
        .bind(p.id)
        .fetch_one(&state.db)
        .await
        .unwrap_or(0)
            > 0
    } else {
        false
    };

    let csrf = get_or_create_csrf_token(&session).await;
    let mut ctx = build_base_ctx(&state, &session).await;
    ctx.insert("offer", &offer);
    ctx.insert("event", &event);
    ctx.insert("driver_username", &driver_username);
    ctx.insert("riders", &riders);
    ctx.insert("rider_count", &rider_count);
    ctx.insert("seats_remaining", &seats_remaining);
    ctx.insert("is_full", &is_full);
    ctx.insert("participant", &participant);
    ctx.insert("is_driver", &is_driver);
    ctx.insert("is_rider", &is_rider);
    ctx.insert("csrf_token", &csrf);
    render(&state.tera, "carpool/offer.html", &ctx)
}

// ── Create new offer ──────────────────────────────────────────────────────────

pub async fn new_offer_get(
    State(state): State<AppState>,
    session: Session,
) -> Result<impl IntoResponse, AppError> {
    get_current_user(&session, &state.db)
        .await
        .ok_or(AppError::Unauthorized)?;

    let event = sqlx::query_as::<_, Event>("SELECT * FROM events WHERE is_active = 1 LIMIT 1")
        .fetch_optional(&state.db)
        .await?
        .ok_or(AppError::BadRequest("No active event.".into()))?;

    let csrf = get_or_create_csrf_token(&session).await;
    let mut ctx = build_base_ctx(&state, &session).await;
    ctx.insert("event", &event);
    ctx.insert("csrf_token", &csrf);
    ctx.insert("errors", &Vec::<String>::new());
    render(&state.tera, "carpool/new_offer.html", &ctx)
}

#[derive(Deserialize)]
pub struct NewOfferForm {
    pub origin_city: String,
    pub origin_state: String,
    pub total_seats: i64,
    pub notes: String,
    pub contact_email: String,
    pub csrf_token: String,
}

pub async fn new_offer_post(
    State(state): State<AppState>,
    session: Session,
    Form(form): Form<NewOfferForm>,
) -> Result<Response, AppError> {
    if !validate_csrf(&session, &form.csrf_token).await {
        return Err(AppError::BadRequest("Invalid CSRF token.".into()));
    }

    let user = get_current_user(&session, &state.db)
        .await
        .ok_or(AppError::Unauthorized)?;

    let event = sqlx::query_as::<_, Event>("SELECT * FROM events WHERE is_active = 1 LIMIT 1")
        .fetch_optional(&state.db)
        .await?
        .ok_or(AppError::BadRequest("No active event.".into()))?;

    // Participant must be registered (paid) for the event
    let participant = sqlx::query_as::<_, Participant>("SELECT * FROM participants WHERE user_id = ? AND event_id = ?")
        .bind(user.id)
        .bind(event.id)
    .fetch_optional(&state.db)
    .await?
    .ok_or(AppError::BadRequest(
        "You must be a registered participant to offer a carpool.".into(),
    ))?;

    let mut errors: Vec<String> = Vec::new();
    if form.origin_city.trim().is_empty() {
        errors.push("Origin city is required.".into());
    }
    if form.origin_state.trim().is_empty() {
        errors.push("Origin state is required.".into());
    }
    let total_seats = form.total_seats.max(1).min(20);

    if !errors.is_empty() {
        let csrf = get_or_create_csrf_token(&session).await;
        let mut ctx = build_base_ctx(&state, &session).await;
        ctx.insert("event", &event);
        ctx.insert("csrf_token", &csrf);
        ctx.insert("errors", &errors);
        return Ok(render(&state.tera, "carpool/new_offer.html", &ctx)?.into_response());
    }

    let contact_email = if form.contact_email.trim().is_empty() {
        user.email.clone()
    } else {
        form.contact_email.clone()
    };

    let row = sqlx::query!(
        r#"
        INSERT INTO carpool_offers
            (driver_id, event_id, origin_city, origin_state, total_seats, notes, contact_email)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        RETURNING id
        "#,
        participant.id,
        event.id,
        form.origin_city,
        form.origin_state,
        total_seats,
        form.notes,
        contact_email
    )
    .fetch_one(&state.db)
    .await?;

    Ok(Redirect::to(&format!("/carpool/offer/{}", row.id)).into_response())
}

// ── Join an offer ─────────────────────────────────────────────────────────────

#[derive(Deserialize)]
pub struct JoinForm {
    pub csrf_token: String,
}

pub async fn join_offer(
    State(state): State<AppState>,
    session: Session,
    Path(offer_id): Path<i64>,
    Form(form): Form<JoinForm>,
) -> Result<Response, AppError> {
    if !validate_csrf(&session, &form.csrf_token).await {
        return Err(AppError::BadRequest("Invalid CSRF token.".into()));
    }

    let user = get_current_user(&session, &state.db)
        .await
        .ok_or(AppError::Unauthorized)?;

    let offer = sqlx::query_as::<_, CarpoolOffer>("SELECT * FROM carpool_offers WHERE id = ?")
        .bind(offer_id)
        .fetch_optional(&state.db)
        .await?
        .ok_or(AppError::NotFound)?;

    let participant = sqlx::query_as::<_, Participant>("SELECT * FROM participants WHERE user_id = ? AND event_id = ?")
        .bind(user.id)
        .bind(offer.event_id)
    .fetch_optional(&state.db)
    .await?
    .ok_or(AppError::BadRequest(
        "You must be registered for this event to join a carpool.".into(),
    ))?;

    if participant.id == offer.driver_id {
        return Err(AppError::BadRequest("You cannot join your own carpool offer.".into()));
    }

    let rider_count: i64 =
        sqlx::query_scalar::<_, i64>("SELECT COUNT(*) FROM carpool_riders WHERE offer_id = ?")
        .bind(offer_id)
            .fetch_one(&state.db)
            .await.unwrap_or(0) as i64;

    if rider_count >= offer.total_seats {
        return Err(AppError::BadRequest("This carpool offer is full.".into()));
    }

    sqlx::query!(
        "INSERT OR IGNORE INTO carpool_riders (rider_id, offer_id) VALUES (?, ?)",
        participant.id,
        offer_id
    )
    .execute(&state.db)
    .await?;

    Ok(Redirect::to(&format!("/carpool/offer/{offer_id}")).into_response())
}

// ── Leave an offer ────────────────────────────────────────────────────────────

pub async fn leave_offer(
    State(state): State<AppState>,
    session: Session,
    Path(offer_id): Path<i64>,
    Form(form): Form<JoinForm>,
) -> Result<Response, AppError> {
    if !validate_csrf(&session, &form.csrf_token).await {
        return Err(AppError::BadRequest("Invalid CSRF token.".into()));
    }

    let user = get_current_user(&session, &state.db)
        .await
        .ok_or(AppError::Unauthorized)?;

    let offer = sqlx::query_as::<_, CarpoolOffer>("SELECT * FROM carpool_offers WHERE id = ?")
        .bind(offer_id)
        .fetch_optional(&state.db)
        .await?
        .ok_or(AppError::NotFound)?;

    let participant = sqlx::query_as::<_, Participant>("SELECT * FROM participants WHERE user_id = ? AND event_id = ?")
        .bind(user.id)
        .bind(offer.event_id)
    .fetch_optional(&state.db)
    .await?
    .ok_or(AppError::BadRequest("Not registered for this event.".into()))?;

    sqlx::query!(
        "DELETE FROM carpool_riders WHERE offer_id = ? AND rider_id = ?",
        offer_id,
        participant.id
    )
    .execute(&state.db)
    .await?;

    Ok(Redirect::to(&format!("/carpool/offer/{offer_id}")).into_response())
}

// ── Delete an offer (driver only) ─────────────────────────────────────────────

pub async fn delete_offer(
    State(state): State<AppState>,
    session: Session,
    Path(offer_id): Path<i64>,
    Form(form): Form<JoinForm>,
) -> Result<Response, AppError> {
    if !validate_csrf(&session, &form.csrf_token).await {
        return Err(AppError::BadRequest("Invalid CSRF token.".into()));
    }

    let user = get_current_user(&session, &state.db)
        .await
        .ok_or(AppError::Unauthorized)?;

    let offer = sqlx::query_as::<_, CarpoolOffer>("SELECT * FROM carpool_offers WHERE id = ?")
        .bind(offer_id)
        .fetch_optional(&state.db)
        .await?
        .ok_or(AppError::NotFound)?;

    let participant = sqlx::query_as::<_, Participant>("SELECT * FROM participants WHERE user_id = ? AND event_id = ?")
        .bind(user.id)
        .bind(offer.event_id)
    .fetch_optional(&state.db)
    .await?
    .ok_or(AppError::Forbidden)?;

    if participant.id != offer.driver_id {
        return Err(AppError::Forbidden);
    }

    sqlx::query!("DELETE FROM carpool_riders WHERE offer_id = ?", offer_id)
        .execute(&state.db)
        .await?;
    sqlx::query!("DELETE FROM carpool_offers WHERE id = ?", offer_id)
        .execute(&state.db)
        .await?;

    Ok(Redirect::to("/carpool").into_response())
}
