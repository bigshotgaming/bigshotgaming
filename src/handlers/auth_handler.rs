use axum::{
    extract::{Form, State},
    response::{Html, IntoResponse, Redirect, Response},
};
use serde::Deserialize;
use tower_sessions::Session;

use crate::{
    auth::{
        get_current_user, get_or_create_csrf_token, hash_password, validate_csrf,
        verify_password, SESSION_USER_ID_KEY,
    },
    error::{render, AppError},
    models::User,
    state::AppState,
};

// ── Login ────────────────────────────────────────────────────────────────────

pub async fn login_get(
    State(state): State<AppState>,
    session: Session,
) -> Result<impl IntoResponse, AppError> {
    let csrf = get_or_create_csrf_token(&session).await;
    let mut ctx = build_auth_ctx(&state);
    ctx.insert("csrf_token", &csrf);
    ctx.insert("errors", &Vec::<String>::new());
    render(&state.tera, "auth/login.html", &ctx)
}

#[derive(Deserialize)]
pub struct LoginForm {
    pub username: String,
    pub password: String,
    pub csrf_token: String,
    pub next: Option<String>,
}

pub async fn login_post(
    State(state): State<AppState>,
    session: Session,
    Form(form): Form<LoginForm>,
) -> Result<Response, AppError> {
    if !validate_csrf(&session, &form.csrf_token).await {
        return Err(AppError::BadRequest("Invalid CSRF token.".into()));
    }

    let user = sqlx::query_as::<_, User>(
        "SELECT * FROM users WHERE username = ? COLLATE NOCASE AND is_active = 1",
    )
    .bind(&form.username)
    .fetch_optional(&state.db)
    .await?;

    if let Some(u) = user {
        if verify_password(&form.password, &u.password_hash) {
            session.insert(SESSION_USER_ID_KEY, u.id).await.ok();
            let next = form.next.as_deref().unwrap_or("/");
            return Ok(Redirect::to(next).into_response());
        }
    }

    let csrf = get_or_create_csrf_token(&session).await;
    let mut ctx = build_auth_ctx(&state);
    ctx.insert("csrf_token", &csrf);
    ctx.insert("errors", &vec!["Invalid username or password."]);
    Ok(render(&state.tera, "auth/login.html", &ctx)?.into_response())
}

// ── Logout ───────────────────────────────────────────────────────────────────

pub async fn logout(session: Session) -> impl IntoResponse {
    session.flush().await.ok();
    Redirect::to("/")
}

// ── Register ─────────────────────────────────────────────────────────────────

pub async fn register_get(
    State(state): State<AppState>,
    session: Session,
) -> Result<impl IntoResponse, AppError> {
    let csrf = get_or_create_csrf_token(&session).await;
    let mut ctx = build_auth_ctx(&state);
    ctx.insert("csrf_token", &csrf);
    ctx.insert("errors", &Vec::<String>::new());
    render(&state.tera, "auth/register.html", &ctx)
}

#[derive(Deserialize)]
pub struct RegisterForm {
    pub username: String,
    pub email: String,
    pub password1: String,
    pub password2: String,
    pub csrf_token: String,
}

pub async fn register_post(
    State(state): State<AppState>,
    session: Session,
    Form(form): Form<RegisterForm>,
) -> Result<Response, AppError> {
    if !validate_csrf(&session, &form.csrf_token).await {
        return Err(AppError::BadRequest("Invalid CSRF token.".into()));
    }

    let mut errors: Vec<String> = Vec::new();

    if form.username.trim().is_empty() {
        errors.push("Username is required.".into());
    }
    if form.password1 != form.password2 {
        errors.push("Passwords do not match.".into());
    }
    if form.password1.len() < 8 {
        errors.push("Password must be at least 8 characters.".into());
    }
    if !form.email.contains('@') {
        errors.push("Enter a valid email address.".into());
    }

    if errors.is_empty() {
        let existing: i64 = sqlx::query_scalar::<_, i64>(
            "SELECT COUNT(*) FROM users WHERE username = ? COLLATE NOCASE OR email = ? COLLATE NOCASE",
        )
        .bind(&form.username)
        .bind(&form.email)
        .fetch_one(&state.db)
        .await
        .unwrap_or(0);

        if existing > 0 {
            errors.push("A user with that username or email already exists.".into());
        }
    }

    if !errors.is_empty() {
        let csrf = get_or_create_csrf_token(&session).await;
        let mut ctx = build_auth_ctx(&state);
        ctx.insert("csrf_token", &csrf);
        ctx.insert("errors", &errors);
        ctx.insert("form_username", &form.username);
        ctx.insert("form_email", &form.email);
        return Ok(render(&state.tera, "auth/register.html", &ctx)?.into_response());
    }

    let hash = hash_password(&form.password1)
        .map_err(|e| AppError::BadRequest(e.to_string()))?;

    let row = sqlx::query!(
        "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?) RETURNING id",
        form.username,
        form.email,
        hash
    )
    .fetch_one(&state.db)
    .await?;

    session.insert(SESSION_USER_ID_KEY, row.id).await.ok();
    Ok(Redirect::to("/").into_response())
}

// ── Password Change ──────────────────────────────────────────────────────────

pub async fn password_change_get(
    State(state): State<AppState>,
    session: Session,
) -> Result<impl IntoResponse, AppError> {
    let user = get_current_user(&session, &state.db)
        .await
        .ok_or(AppError::Unauthorized)?;

    let csrf = get_or_create_csrf_token(&session).await;
    let mut ctx = build_auth_ctx(&state);
    ctx.insert("csrf_token", &csrf);
    ctx.insert("current_user", &user);
    ctx.insert("errors", &Vec::<String>::new());
    ctx.insert("is_authenticated", &true);
    render(&state.tera, "auth/password_change.html", &ctx)
}

#[derive(Deserialize)]
pub struct PasswordChangeForm {
    pub old_password: String,
    pub new_password1: String,
    pub new_password2: String,
    pub csrf_token: String,
}

pub async fn password_change_post(
    State(state): State<AppState>,
    session: Session,
    Form(form): Form<PasswordChangeForm>,
) -> Result<Response, AppError> {
    if !validate_csrf(&session, &form.csrf_token).await {
        return Err(AppError::BadRequest("Invalid CSRF token.".into()));
    }
    let user = get_current_user(&session, &state.db)
        .await
        .ok_or(AppError::Unauthorized)?;

    let mut errors: Vec<String> = Vec::new();
    if !verify_password(&form.old_password, &user.password_hash) {
        errors.push("Current password is incorrect.".into());
    }
    if form.new_password1 != form.new_password2 {
        errors.push("New passwords do not match.".into());
    }
    if form.new_password1.len() < 8 {
        errors.push("Password must be at least 8 characters.".into());
    }

    if !errors.is_empty() {
        let csrf = get_or_create_csrf_token(&session).await;
        let mut ctx = build_auth_ctx(&state);
        ctx.insert("csrf_token", &csrf);
        ctx.insert("current_user", &user);
        ctx.insert("is_authenticated", &true);
        ctx.insert("errors", &errors);
        return Ok(render(&state.tera, "auth/password_change.html", &ctx)?.into_response());
    }

    let new_hash = hash_password(&form.new_password1)
        .map_err(|e| AppError::BadRequest(e.to_string()))?;
    sqlx::query!(
        "UPDATE users SET password_hash = ? WHERE id = ?",
        new_hash,
        user.id
    )
    .execute(&state.db)
    .await?;

    Ok(Redirect::to("/").into_response())
}

// ── Helpers ──────────────────────────────────────────────────────────────────

fn build_auth_ctx(state: &AppState) -> tera::Context {
    let mut ctx = tera::Context::new();
    ctx.insert("STATIC_URL", &state.config.static_url);
    ctx.insert("is_authenticated", &false);
    ctx
}
