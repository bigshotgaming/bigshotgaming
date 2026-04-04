use axum::{
    extract::{Form, Path, State},
    response::{IntoResponse, Redirect, Response},
};
use serde::Deserialize;
use tower_sessions::Session;
use uuid::Uuid;

use crate::{
    auth::{get_current_user, get_or_create_csrf_token, validate_csrf},
    error::{render, AppError},
    models::{Coupon, Event, Participant, ParticipantListRow, Venue},
    state::AppState,
};
use crate::handlers::pages::build_base_ctx;

// ── Event Index ───────────────────────────────────────────────────────────────

pub async fn index(
    State(state): State<AppState>,
    session: Session,
) -> Result<impl IntoResponse, AppError> {
    let event = sqlx::query_as::<_, Event>("SELECT * FROM events WHERE is_active = 1 LIMIT 1")
        .fetch_optional(&state.db)
        .await?;

    let venue: Option<Venue> = if let Some(e) = &event {
        if let Some(vid) = e.venue_id {
            sqlx::query_as::<_, Venue>("SELECT * FROM venues WHERE id = ?")
        .bind(vid)
                .fetch_optional(&state.db)
                .await?
        } else {
            None
        }
    } else {
        None
    };

    let (num_paid, num_pending, num_remaining) = if let Some(e) = &event {
        let paid: i64 = sqlx::query_scalar::<_, i64>("SELECT COUNT(*) FROM participants p JOIN coupons c ON c.participant_id = p.id WHERE p.event_id = ? AND c.activated = 1")
        .bind(e.id)
        .fetch_one(&state.db)
        .await
        .unwrap_or(0);
        let pending: i64 = sqlx::query_scalar::<_, i64>("SELECT COUNT(*) FROM participants WHERE event_id = ?")
        .bind(e.id)
        .fetch_one(&state.db)
        .await
        .unwrap_or(0);
        let remaining = e.participant_limit - paid;
        (paid, pending, remaining)
    } else {
        (0i64, 0i64, 0i64)
    };

    let mut ctx = build_base_ctx(&state, &session).await;
    ctx.insert("event", &event);
    ctx.insert("venue", &venue);
    ctx.insert("num_paid", &num_paid);
    ctx.insert("num_pending", &num_pending);
    ctx.insert("num_remaining", &num_remaining);
    render(&state.tera, "events/index.html", &ctx)
}

// ── Register ──────────────────────────────────────────────────────────────────

pub async fn register_get(
    State(state): State<AppState>,
    session: Session,
    Path(event_id): Path<i64>,
) -> Result<impl IntoResponse, AppError> {
    let event = sqlx::query_as::<_, Event>("SELECT * FROM events WHERE id = ?")
        .bind(event_id)
        .fetch_optional(&state.db)
        .await?
        .ok_or(AppError::NotFound)?;

    let user = get_current_user(&session, &state.db).await;
    let participant = if let Some(u) = &user {
        sqlx::query_as::<_, Participant>("SELECT * FROM participants WHERE user_id = ? AND event_id = ?")
        .bind(u.id)
        .bind(event_id)
        .fetch_optional(&state.db)
        .await?
    } else {
        None
    };

    let coupons: Vec<Coupon> = if let Some(p) = &participant {
        sqlx::query_as::<_, Coupon>("SELECT * FROM coupons WHERE participant_id = ?")
        .bind(p.id)
        .fetch_all(&state.db)
        .await?
    } else {
        Vec::new()
    };

    let csrf = get_or_create_csrf_token(&session).await;
    let mut ctx = build_base_ctx(&state, &session).await;
    ctx.insert("event", &event);
    ctx.insert("participant", &participant);
    ctx.insert("coupons", &coupons);
    ctx.insert("csrf_token", &csrf);
    ctx.insert("errors", &Vec::<String>::new());
    render(&state.tera, "events/register.html", &ctx)
}

#[derive(Deserialize)]
pub struct RegisterForm {
    pub quantity: i64,
    pub waiver_accepted: Option<String>,
    pub csrf_token: String,
}

pub async fn register_post(
    State(state): State<AppState>,
    session: Session,
    Path(event_id): Path<i64>,
    Form(form): Form<RegisterForm>,
) -> Result<Response, AppError> {
    if !validate_csrf(&session, &form.csrf_token).await {
        return Err(AppError::BadRequest("Invalid CSRF token.".into()));
    }

    let user = get_current_user(&session, &state.db)
        .await
        .ok_or(AppError::Unauthorized)?;

    let event = sqlx::query_as::<_, Event>("SELECT * FROM events WHERE id = ?")
        .bind(event_id)
        .fetch_optional(&state.db)
        .await?
        .ok_or(AppError::NotFound)?;

    if event.is_active == 0 {
        return Err(AppError::BadRequest("This event is not active.".into()));
    }
    if event.registration_enabled == 0 {
        return Err(AppError::BadRequest("Registration is currently closed.".into()));
    }

    let quantity = form.quantity.clamp(1, 20);

    let participant = sqlx::query_as::<_, Participant>("SELECT * FROM participants WHERE user_id = ? AND event_id = ?")
        .bind(user.id)
        .bind(event_id)
    .fetch_optional(&state.db)
    .await?;

    let participant = if let Some(p) = participant {
        p
    } else {
        let row = sqlx::query!(
            "INSERT INTO participants (user_id, event_id) VALUES (?, ?) RETURNING id",
            user.id,
            event_id
        )
        .fetch_one(&state.db)
        .await?;
        sqlx::query_as::<_, Participant>("SELECT * FROM participants WHERE id = ?")
        .bind(row.id)
            .fetch_one(&state.db)
            .await?
    };

    session.insert("pending_event_id", event_id).await.ok();
    session.insert("pending_quantity", quantity).await.ok();
    session.insert("pending_participant_id", participant.id).await.ok();

    Ok(Redirect::to(&format!("/events/payment/{event_id}")).into_response())
}

// ── Payment ───────────────────────────────────────────────────────────────────

pub async fn payment_get(
    State(state): State<AppState>,
    session: Session,
    Path(event_id): Path<i64>,
) -> Result<impl IntoResponse, AppError> {
    let user = get_current_user(&session, &state.db)
        .await
        .ok_or(AppError::Unauthorized)?;

    let event = sqlx::query_as::<_, Event>("SELECT * FROM events WHERE id = ?")
        .bind(event_id)
        .fetch_optional(&state.db)
        .await?
        .ok_or(AppError::NotFound)?;

    let quantity: i64 = session
        .get("pending_quantity")
        .await
        .unwrap_or(None)
        .unwrap_or(1);

    let csrf = get_or_create_csrf_token(&session).await;
    let total_cents = (event.prepay_price * 100.0 * quantity as f64) as i64;

    let mut ctx = build_base_ctx(&state, &session).await;
    ctx.insert("event", &event);
    ctx.insert("user", &user);
    ctx.insert("quantity", &quantity);
    ctx.insert("price", &event.prepay_price);
    ctx.insert("total_amount", &total_cents);
    ctx.insert("data_key", &state.config.stripe_publishable_key);
    ctx.insert("csrf_token", &csrf);
    render(&state.tera, "events/payment.html", &ctx)
}

#[derive(Deserialize)]
#[allow(non_snake_case)]
pub struct PaymentForm {
    pub stripeToken: Option<String>,
    pub csrf_token: String,
}

pub async fn payment_post(
    State(state): State<AppState>,
    session: Session,
    Path(event_id): Path<i64>,
    Form(form): Form<PaymentForm>,
) -> Result<Response, AppError> {
    if !validate_csrf(&session, &form.csrf_token).await {
        return Err(AppError::BadRequest("Invalid CSRF token.".into()));
    }

    get_current_user(&session, &state.db)
        .await
        .ok_or(AppError::Unauthorized)?;

    let quantity: i64 = session
        .get("pending_quantity")
        .await
        .unwrap_or(None)
        .unwrap_or(1);
    let participant_id: Option<i64> = session
        .get("pending_participant_id")
        .await
        .unwrap_or(None);

    let stripe_txn = form.stripeToken.as_deref().unwrap_or("manual");
    for i in 0..quantity {
        let coupon_uuid = Uuid::new_v4().to_string();
        let pid: Option<i64> = if i == 0 { participant_id } else { None };
        sqlx::query!(
            "INSERT INTO coupons (uuid, event_id, stripe_transaction, participant_id) VALUES (?, ?, ?, ?)",
            coupon_uuid,
            event_id,
            stripe_txn,
            pid
        )
        .execute(&state.db)
        .await?;
    }

    Ok(Redirect::to(&format!("/events/register/{event_id}")).into_response())
}

// ── Participants List ─────────────────────────────────────────────────────────

pub async fn participants(
    State(state): State<AppState>,
    session: Session,
    Path(event_id): Path<i64>,
) -> Result<impl IntoResponse, AppError> {
    let event = sqlx::query_as::<_, Event>("SELECT * FROM events WHERE id = ?")
        .bind(event_id)
        .fetch_optional(&state.db)
        .await?
        .ok_or(AppError::NotFound)?;

    let participants = sqlx::query_as::<_, ParticipantListRow>(r#"
        SELECT p.id, p.user_id, p.event_id, p.signup_time, p.checked_in, p.checkin_time,
               u.username,
               CAST(COALESCE((SELECT COUNT(*) FROM coupons c WHERE c.participant_id = p.id AND c.activated = 1), 0) AS INTEGER) as "coupon_count: i64"
          FROM participants p
          JOIN users u ON u.id = p.user_id
         WHERE p.event_id = ?
         ORDER BY p.signup_time
        "#)
        .bind(event_id)
    .fetch_all(&state.db)
    .await?;

    let mut ctx = build_base_ctx(&state, &session).await;
    ctx.insert("event", &event);
    ctx.insert("participants", &participants);
    render(&state.tera, "events/participants.html", &ctx)
}

// ── Coupon Activation ─────────────────────────────────────────────────────────

pub async fn activate_get(
    State(state): State<AppState>,
    session: Session,
    Path((event_id, coupon_uuid)): Path<(i64, String)>,
) -> Result<impl IntoResponse, AppError> {
    let event = sqlx::query_as::<_, Event>("SELECT * FROM events WHERE id = ?")
        .bind(event_id)
        .fetch_optional(&state.db)
        .await?
        .ok_or(AppError::NotFound)?;

    let coupon = sqlx::query_as::<_, Coupon>("SELECT * FROM coupons WHERE uuid = ? AND event_id = ?")
        .bind(coupon_uuid)
        .bind(event_id)
    .fetch_optional(&state.db)
    .await?
    .ok_or(AppError::NotFound)?;

    if coupon.activated != 0 {
        let mut ctx = build_base_ctx(&state, &session).await;
        ctx.insert("event", &event);
        return render(&state.tera, "events/already_activated.html", &ctx);
    }

    let csrf = get_or_create_csrf_token(&session).await;
    let mut ctx = build_base_ctx(&state, &session).await;
    ctx.insert("event", &event);
    ctx.insert("coupon", &coupon);
    ctx.insert("csrf_token", &csrf);
    ctx.insert("errors", &Vec::<String>::new());
    render(&state.tera, "events/activate.html", &ctx)
}

#[derive(Deserialize)]
pub struct ActivateForm {
    pub waiver_name: String,
    pub waiver_accepted: Option<String>,
    pub csrf_token: String,
}

pub async fn activate_post(
    State(state): State<AppState>,
    session: Session,
    Path((event_id, coupon_uuid)): Path<(i64, String)>,
    Form(form): Form<ActivateForm>,
) -> Result<Response, AppError> {
    if !validate_csrf(&session, &form.csrf_token).await {
        return Err(AppError::BadRequest("Invalid CSRF token.".into()));
    }

    let user = get_current_user(&session, &state.db)
        .await
        .ok_or(AppError::Unauthorized)?;

    let coupon = sqlx::query_as::<_, Coupon>("SELECT * FROM coupons WHERE uuid = ? AND event_id = ?")
        .bind(&coupon_uuid)
        .bind(event_id)
    .fetch_optional(&state.db)
    .await?
    .ok_or(AppError::NotFound)?;

    if coupon.activated != 0 {
        let event = sqlx::query_as::<_, Event>("SELECT * FROM events WHERE id = ?")
        .bind(event_id)
            .fetch_optional(&state.db)
            .await?
            .ok_or(AppError::NotFound)?;
        let mut ctx = build_base_ctx(&state, &session).await;
        ctx.insert("event", &event);
        return Ok(render(&state.tera, "events/coupon_used.html", &ctx)?.into_response());
    }

    let participant = sqlx::query_as::<_, Participant>("SELECT * FROM participants WHERE user_id = ? AND event_id = ?")
        .bind(user.id)
        .bind(event_id)
    .fetch_optional(&state.db)
    .await?;

    let participant_id = if let Some(p) = participant {
        p.id
    } else {
        sqlx::query!(
            "INSERT INTO participants (user_id, event_id) VALUES (?, ?) RETURNING id",
            user.id,
            event_id
        )
        .fetch_one(&state.db)
        .await?
        .id
    };

    let now = chrono::Utc::now().to_rfc3339();
    sqlx::query!(
        "UPDATE coupons SET activated = 1, activated_time = ?, participant_id = ? WHERE uuid = ?",
        now,
        participant_id,
        coupon_uuid
    )
    .execute(&state.db)
    .await?;

    if !form.waiver_name.is_empty() {
        sqlx::query!(
            "INSERT INTO waivers (participant_id, name) VALUES (?, ?)",
            participant_id,
            form.waiver_name
        )
        .execute(&state.db)
        .await?;
    }

    let event = sqlx::query_as::<_, Event>("SELECT * FROM events WHERE id = ?")
        .bind(event_id)
        .fetch_optional(&state.db)
        .await?
        .ok_or(AppError::NotFound)?;
    let mut ctx = build_base_ctx(&state, &session).await;
    ctx.insert("event", &event);
    Ok(render(&state.tera, "events/activated.html", &ctx)?.into_response())
}


