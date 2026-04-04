use axum::{
    extract::{Form, Path, Query, State},
    response::{IntoResponse, Redirect, Response},
};
use serde::Deserialize;
use tower_sessions::Session;

use crate::{
    auth::{get_current_user, get_or_create_csrf_token},
    error::{render, AppError},
    models::{PostRow, Sponsor},
    state::AppState,
};

// ── Index / News ─────────────────────────────────────────────────────────────

#[derive(Deserialize)]
pub struct PageQuery {
    pub page: Option<i64>,
}

pub async fn index(
    State(state): State<AppState>,
    session: Session,
    Query(q): Query<PageQuery>,
) -> Result<impl IntoResponse, AppError> {
    let page = q.page.unwrap_or(1).max(1);
    let per_page: i64 = 5;
    let offset = (page - 1) * per_page;

    let posts = sqlx::query_as::<_, PostRow>(r#"
        SELECT p.id, p.title, p.body, p.created_time, p.author_id, p.category,
               u.username as author_username
          FROM posts p
          JOIN users u ON u.id = p.author_id
         WHERE p.category = 'N'
         ORDER BY p.created_time DESC
         LIMIT ? OFFSET ?
        "#)
        .bind(per_page)
        .bind(offset)
    .fetch_all(&state.db)
    .await?;

    let total: i64 = sqlx::query_scalar::<_, i64>("SELECT COUNT(*) FROM posts WHERE category = 'N'")
    .fetch_one(&state.db)
    .await
        .unwrap_or(0);

    let num_pages = ((total + per_page - 1) / per_page).max(1);
    let has_previous = page > 1;
    let has_next = page < num_pages;

    let mut ctx = build_base_ctx(&state, &session).await;
    ctx.insert("posts", &posts);
    ctx.insert("page", &page);
    ctx.insert("num_pages", &num_pages);
    ctx.insert("has_previous", &has_previous);
    ctx.insert("has_next", &has_next);
    ctx.insert("prev_page", &(page - 1));
    ctx.insert("next_page", &(page + 1));

    render(&state.tera, "index.html", &ctx)
}

// ── Reviews ──────────────────────────────────────────────────────────────────

pub async fn reviews(
    State(state): State<AppState>,
    session: Session,
    Query(q): Query<PageQuery>,
) -> Result<impl IntoResponse, AppError> {
    let page = q.page.unwrap_or(1).max(1);
    let per_page: i64 = 5;
    let offset = (page - 1) * per_page;

    let posts = sqlx::query_as::<_, PostRow>(r#"
        SELECT p.id, p.title, p.body, p.created_time, p.author_id, p.category,
               u.username as author_username
          FROM posts p
          JOIN users u ON u.id = p.author_id
         WHERE p.category = 'R'
         ORDER BY p.created_time DESC
         LIMIT ? OFFSET ?
        "#)
        .bind(per_page)
        .bind(offset)
    .fetch_all(&state.db)
    .await?;

    let total: i64 =
        sqlx::query_scalar::<_, i64>("SELECT COUNT(*) FROM posts WHERE category = 'R'")
            .fetch_one(&state.db)
            .await.unwrap_or(0) as i64;

    let num_pages = ((total + per_page - 1) / per_page).max(1);
    let mut ctx = build_base_ctx(&state, &session).await;
    ctx.insert("posts", &posts);
    ctx.insert("page", &page);
    ctx.insert("num_pages", &num_pages);
    ctx.insert("has_previous", &(page > 1));
    ctx.insert("has_next", &(page < num_pages));
    ctx.insert("prev_page", &(page - 1));
    ctx.insert("next_page", &(page + 1));

    render(&state.tera, "reviews.html", &ctx)
}

// ── Single Post ──────────────────────────────────────────────────────────────

pub async fn post_detail(
    State(state): State<AppState>,
    session: Session,
    Path(pk): Path<i64>,
) -> Result<impl IntoResponse, AppError> {
    let row = sqlx::query_as::<_, PostRow>(r#"
        SELECT p.id, p.title, p.body, p.created_time, p.author_id, p.category,
               u.username as author_username
          FROM posts p
          JOIN users u ON u.id = p.author_id
         WHERE p.id = ?
        "#)
        .bind(pk)
    .fetch_optional(&state.db)
    .await?
    .ok_or(AppError::NotFound)?;

    let mut ctx = build_base_ctx(&state, &session).await;
    ctx.insert("post", &row);
    render(&state.tera, "post.html", &ctx)
}

// ── Contact ──────────────────────────────────────────────────────────────────

pub async fn contact_get(
    State(state): State<AppState>,
    session: Session,
) -> Result<impl IntoResponse, AppError> {
    let csrf = get_or_create_csrf_token(&session).await;
    let mut ctx = build_base_ctx(&state, &session).await;
    ctx.insert("csrf_token", &csrf);
    ctx.insert("errors", &Vec::<String>::new());
    ctx.insert("success", &false);
    render(&state.tera, "contact.html", &ctx)
}

#[derive(Deserialize)]
pub struct ContactForm {
    pub subject: String,
    pub message: String,
    pub csrf_token: String,
}

pub async fn contact_post(
    State(state): State<AppState>,
    session: Session,
    Form(form): Form<ContactForm>,
) -> Result<impl IntoResponse, AppError> {
    if !crate::auth::validate_csrf(&session, &form.csrf_token).await {
        return Err(AppError::BadRequest("Invalid CSRF token.".into()));
    }
    let mut ctx = build_base_ctx(&state, &session).await;
    let csrf = get_or_create_csrf_token(&session).await;
    ctx.insert("csrf_token", &csrf);
    ctx.insert("errors", &Vec::<String>::new());
    ctx.insert("success", &true);
    render(&state.tera, "contact.html", &ctx)
}

// ── Volunteer ────────────────────────────────────────────────────────────────

pub async fn volunteer_get(
    State(state): State<AppState>,
    session: Session,
) -> Result<impl IntoResponse, AppError> {
    let csrf = get_or_create_csrf_token(&session).await;
    let mut ctx = build_base_ctx(&state, &session).await;
    ctx.insert("csrf_token", &csrf);
    ctx.insert("errors", &Vec::<String>::new());
    ctx.insert("success", &false);
    render(&state.tera, "volunteer.html", &ctx)
}

#[derive(Deserialize)]
pub struct VolunteerForm {
    pub name: String,
    pub location: String,
    pub cmu_student: Option<String>,
    pub desired_position: String,
    pub comments: String,
    pub csrf_token: String,
}

pub async fn volunteer_post(
    State(state): State<AppState>,
    session: Session,
    Form(form): Form<VolunteerForm>,
) -> Result<impl IntoResponse, AppError> {
    if !crate::auth::validate_csrf(&session, &form.csrf_token).await {
        return Err(AppError::BadRequest("Invalid CSRF token.".into()));
    }
    let csrf = get_or_create_csrf_token(&session).await;
    let mut ctx = build_base_ctx(&state, &session).await;
    ctx.insert("csrf_token", &csrf);
    ctx.insert("errors", &Vec::<String>::new());
    ctx.insert("success", &true);
    render(&state.tera, "volunteer.html", &ctx)
}

// ── Sponsors ─────────────────────────────────────────────────────────────────

pub async fn sponsors(
    State(state): State<AppState>,
    session: Session,
) -> Result<impl IntoResponse, AppError> {
    let event_id: Option<i64> = sqlx::query_scalar::<_, i64>("SELECT id FROM events WHERE is_active = 1 LIMIT 1")
    .fetch_optional(&state.db)
    .await?;

    let sponsors = if let Some(eid) = event_id {
        sqlx::query_as::<_, Sponsor>(r#"
            SELECT s.*
              FROM sponsors s
              JOIN event_sponsors es ON es.sponsor_id = s.id
             WHERE es.event_id = ? AND es.status = 'c'
             ORDER BY s.featured_sponsor DESC, s.name
            "#)
        .bind(eid)
        .fetch_all(&state.db)
        .await?
    } else {
        Vec::new()
    };

    let mut ctx = build_base_ctx(&state, &session).await;
    ctx.insert("sponsors", &sponsors);
    render(&state.tera, "sponsors.html", &ctx)
}

// ── Shared context builder ────────────────────────────────────────────────────

pub async fn build_base_ctx(state: &AppState, session: &Session) -> tera::Context {
    let mut ctx = tera::Context::new();
    ctx.insert("STATIC_URL", &state.config.static_url);

    // Current user
    if let Some(user) = get_current_user(session, &state.db).await {
        ctx.insert("user", &user);
        ctx.insert("is_authenticated", &true);
    } else {
        ctx.insert("is_authenticated", &false);
    }

    // Active event info for lan_info sidebar
    if let Ok(Some(event)) = sqlx::query_as::<_, crate::models::Event>("SELECT * FROM events WHERE is_active = 1 LIMIT 1")
    .fetch_optional(&state.db)
    .await
    {
        let num_paid: i64 = sqlx::query_scalar::<_, i64>("SELECT COUNT(*) FROM participants p JOIN coupons c ON c.participant_id = p.id WHERE p.event_id = ? AND c.activated = 1")
        .bind(event.id)
        .fetch_one(&state.db)
        .await
        .unwrap_or(0);

        let num_pending: i64 = sqlx::query_scalar::<_, i64>("SELECT COUNT(*) FROM participants WHERE event_id = ?")
        .bind(event.id)
        .fetch_one(&state.db)
        .await
        .unwrap_or(0);

        let num_remaining = event.participant_limit - num_paid;

        ctx.insert("active_event_id", &event.id);
        ctx.insert("active_event_name", &event.name);
        ctx.insert("active_event_start", &event.start_date);
        ctx.insert("active_event_end", &event.end_date);
        ctx.insert("active_event_num_paid", &num_paid);
        ctx.insert("active_event_num_pending", &num_pending);
        ctx.insert("active_event_num_remaining", &num_remaining);
        ctx.insert("active_event_registration_enabled", &(event.registration_enabled != 0));
    }

    ctx
}
