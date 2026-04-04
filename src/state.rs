use sqlx::SqlitePool;
use std::sync::Arc;
use tera::Tera;

use crate::config::Config;

#[derive(Clone)]
pub struct AppState {
    pub db: SqlitePool,
    pub tera: Arc<Tera>,
    pub config: Arc<Config>,
}
