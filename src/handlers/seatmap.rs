use axum::{
    extract::{Path, State},
    response::{IntoResponse, Json},
};
use tower_sessions::Session;

use crate::{
    auth::get_current_user,
    error::{render, AppError},
    models::{Event, Seat, SeatMap, SeatTable},
    state::AppState,
};
use crate::handlers::pages::build_base_ctx;

pub async fn display(
    State(state): State<AppState>,
    session: Session,
) -> Result<impl IntoResponse, AppError> {
    let event = sqlx::query_as::<_, Event>("SELECT * FROM events WHERE is_active = 1 LIMIT 1")
        .fetch_optional(&state.db)
        .await?;

    let (seatmap_id, seat_size) = if let Some(ref e) = event {
        let sm = sqlx::query_as::<_, SeatMap>("SELECT * FROM seatmaps WHERE event_id = ?")
        .bind(e.id)
            .fetch_optional(&state.db)
            .await?;
        if let Some(sm) = sm {
            (Some(sm.id), sm.seat_size)
        } else {
            (None, 30i64)
        }
    } else {
        (None, 30i64)
    };

    let user = get_current_user(&session, &state.db).await;
    let username = user.as_ref().map(|u| u.username.clone()).unwrap_or_default();

    let (seat_data_json, table_data_json) = if let Some(smid) = seatmap_id {
        let seats = sqlx::query_as::<_, Seat>("SELECT * FROM seats WHERE seatmap_id = ?")
        .bind(smid)
            .fetch_all(&state.db)
            .await?;
        let tables = sqlx::query_as::<_, SeatTable>("SELECT * FROM seat_tables WHERE seatmap_id = ?")
        .bind(smid)
            .fetch_all(&state.db)
            .await?;
        (
            serde_json::to_string(&seats).unwrap_or_default(),
            serde_json::to_string(&tables).unwrap_or_default(),
        )
    } else {
        (String::new(), String::new())
    };

    let mut ctx = build_base_ctx(&state, &session).await;
    ctx.insert("seatmap_id", &seatmap_id);
    ctx.insert("seat_size", &seat_size);
    ctx.insert("seat_data", &seat_data_json);
    ctx.insert("table_data", &table_data_json);
    ctx.insert("username", &username);
    render(&state.tera, "seatmap/seatmap_page.html", &ctx)
}

/// JSON API: return seatmap data for the active event's seatmap.
pub async fn data(
    State(state): State<AppState>,
    Path(seatmap_id): Path<i64>,
) -> Result<impl IntoResponse, AppError> {
    let seats = sqlx::query_as::<_, Seat>("SELECT * FROM seats WHERE seatmap_id = ?")
        .bind(seatmap_id)
        .fetch_all(&state.db)
        .await?;
    let tables = sqlx::query_as::<_, SeatTable>("SELECT * FROM seat_tables WHERE seatmap_id = ?")
        .bind(seatmap_id)
        .fetch_all(&state.db)
        .await?;
    let sm = sqlx::query_as::<_, SeatMap>("SELECT * FROM seatmaps WHERE id = ?")
        .bind(seatmap_id)
        .fetch_optional(&state.db)
        .await?
        .ok_or(AppError::NotFound)?;

    Ok(Json(serde_json::json!({
        "seats": seats,
        "tables": tables,
        "seat_size": sm.seat_size,
    })))
}

/// Claim a seat for the current user.
pub async fn claim_seat(
    State(state): State<AppState>,
    session: Session,
    Path(seat_id): Path<i64>,
) -> Result<impl IntoResponse, AppError> {
    let user = get_current_user(&session, &state.db)
        .await
        .ok_or(AppError::Unauthorized)?;

    let seat = sqlx::query_as::<_, Seat>("SELECT * FROM seats WHERE id = ?")
        .bind(seat_id)
        .fetch_optional(&state.db)
        .await?
        .ok_or(AppError::NotFound)?;

    if seat.status != "O" {
        return Err(AppError::BadRequest("Seat is not open.".into()));
    }

    // Find participant for this user and event
    let sm = sqlx::query_as::<_, SeatMap>("SELECT * FROM seatmaps WHERE id = ?")
        .bind(seat.seatmap_id)
        .fetch_one(&state.db)
        .await?;

    let participant = sqlx::query!(
        "SELECT id FROM participants p JOIN coupons c ON c.participant_id = p.id WHERE p.user_id = ? AND p.event_id = ? AND c.activated = 1 LIMIT 1",
        user.id,
        sm.event_id
    )
    .fetch_optional(&state.db)
    .await?;

    if participant.is_none() {
        return Err(AppError::Forbidden);
    }
    let participant_id = participant.unwrap().id;

    // Free any existing seat for this participant
    sqlx::query!(
        "UPDATE seats SET status = 'O', participant_id = NULL WHERE participant_id = ? AND seatmap_id = ?",
        participant_id,
        seat.seatmap_id
    )
    .execute(&state.db)
    .await?;

    // Claim the new seat
    sqlx::query!(
        "UPDATE seats SET status = 'T', participant_id = ? WHERE id = ?",
        participant_id,
        seat_id
    )
    .execute(&state.db)
    .await?;

    Ok(Json(serde_json::json!({ "status": "ok" })))
}
