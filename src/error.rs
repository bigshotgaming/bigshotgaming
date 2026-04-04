use axum::{
    http::StatusCode,
    response::{Html, IntoResponse, Response},
};
use tera::Tera;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum AppError {
    #[error("Database error: {0}")]
    Database(#[from] sqlx::Error),

    #[error("Template error: {0}")]
    Template(#[from] tera::Error),

    #[error("Anyhow error: {0}")]
    Anyhow(#[from] anyhow::Error),

    #[error("Not found")]
    NotFound,

    #[error("Unauthorized")]
    Unauthorized,

    #[error("Forbidden")]
    Forbidden,

    #[error("Bad request: {0}")]
    BadRequest(String),
}

impl IntoResponse for AppError {
    fn into_response(self) -> Response {
        let (status, message) = match &self {
            AppError::NotFound => (StatusCode::NOT_FOUND, "Page not found.".to_string()),
            AppError::Unauthorized => (StatusCode::UNAUTHORIZED, "You must be logged in.".to_string()),
            AppError::Forbidden => (StatusCode::FORBIDDEN, "You do not have permission to view this page.".to_string()),
            AppError::BadRequest(msg) => (StatusCode::BAD_REQUEST, msg.clone()),
            AppError::Database(e) => {
                tracing::error!("Database error: {e}");
                (StatusCode::INTERNAL_SERVER_ERROR, "A database error occurred.".to_string())
            }
            AppError::Template(e) => {
                tracing::error!("Template error: {e}");
                (StatusCode::INTERNAL_SERVER_ERROR, "A template rendering error occurred.".to_string())
            }
            AppError::Anyhow(e) => {
                tracing::error!("Internal error: {e}");
                (StatusCode::INTERNAL_SERVER_ERROR, "An internal error occurred.".to_string())
            }
        };

        let body = format!(
            "<!DOCTYPE html><html><body><h1>{}</h1><p>{}</p></body></html>",
            status,
            message
        );
        (status, Html(body)).into_response()
    }
}

/// Render a Tera template to an HTML response, mapping errors to AppError.
pub fn render(tera: &Tera, template: &str, ctx: &tera::Context) -> Result<Html<String>, AppError> {
    let html = tera.render(template, ctx)?;
    Ok(Html(html))
}
