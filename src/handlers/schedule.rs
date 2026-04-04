use axum::{
    extract::{Path, State},
    response::IntoResponse,
};
use std::collections::BTreeMap;
use tower_sessions::Session;

use crate::{
    error::{render, AppError},
    models::{Event, ScheduleItem},
    state::AppState,
};
use crate::handlers::pages::build_base_ctx;

pub async fn index(
    State(state): State<AppState>,
    session: Session,
) -> Result<impl IntoResponse, AppError> {
    let event = sqlx::query_as::<_, Event>("SELECT * FROM events WHERE is_active = 1 LIMIT 1")
        .fetch_optional(&state.db)
        .await?;

    let days: BTreeMap<String, Vec<ScheduleItem>> = if let Some(ref e) = event {
        let items = sqlx::query_as::<_, ScheduleItem>("SELECT * FROM schedule_items WHERE event_id = ? ORDER BY start_time")
        .bind(e.id)
        .fetch_all(&state.db)
        .await?;

        let mut map: BTreeMap<String, Vec<ScheduleItem>> = BTreeMap::new();
        for item in items {
            // Group by date portion of start_time (first 10 chars of ISO string)
            let day = item.start_time.chars().take(10).collect::<String>();
            map.entry(day).or_default().push(item);
        }
        map
    } else {
        BTreeMap::new()
    };

    let mut ctx = build_base_ctx(&state, &session).await;
    ctx.insert("event", &event);
    ctx.insert("days", &days);
    render(&state.tera, "schedule/index.html", &ctx)
}
