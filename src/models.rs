use serde::{Deserialize, Serialize};

// ── Users ────────────────────────────────────────────────────────────────────

#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct User {
    pub id: i64,
    pub username: String,
    pub email: String,
    pub password_hash: String,
    pub first_name: String,
    pub last_name: String,
    pub is_staff: i64,
    pub is_superuser: i64,
    pub is_active: i64,
    pub date_joined: String,
}

// ── Venues & Events ──────────────────────────────────────────────────────────

#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct Venue {
    pub id: i64,
    pub name: String,
    pub address: String,
    pub city: String,
    pub state: String,
    pub zipcode: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct Event {
    pub id: i64,
    pub name: String,
    pub start_date: String,
    pub end_date: String,
    pub venue_id: Option<i64>,
    pub participant_limit: i64,
    pub description: String,
    pub is_active: i64,
    pub registration_enabled: i64,
    pub prepay_price: f64,
    pub atd_price: f64,
    pub waiver_url: Option<String>,
}

/// Event with counts used in listings.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EventWithCounts {
    pub event: Event,
    pub venue: Option<Venue>,
    pub num_paid: i64,
    pub num_pending: i64,
    pub num_remaining: i64,
}

#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct Participant {
    pub id: i64,
    pub user_id: i64,
    pub event_id: i64,
    pub signup_time: String,
    pub checked_in: i64,
    pub checkin_time: Option<String>,
}

/// Named result struct for participant list queries (with username, coupon info).
#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct ParticipantListRow {
    pub id: i64,
    pub user_id: i64,
    pub event_id: i64,
    pub signup_time: String,
    pub checked_in: i64,
    pub checkin_time: Option<String>,
    pub username: String,
    pub coupon_count: i64,
}

#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct Coupon {
    pub uuid: String,
    pub event_id: i64,
    pub stripe_transaction: Option<String>,
    pub activated: i64,
    pub created_time: String,
    pub activated_time: Option<String>,
    pub notes: Option<String>,
    pub participant_id: Option<i64>,
}

#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct Waiver {
    pub id: i64,
    pub participant_id: i64,
    pub name: String,
    pub preferred_name: String,
    pub minor: i64,
    pub minor_age: Option<i64>,
    pub signed_on: String,
}

// ── Pages ────────────────────────────────────────────────────────────────────

#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct Post {
    pub id: i64,
    pub title: String,
    pub body: String,
    pub created_time: String,
    pub author_id: i64,
    pub category: String,
}

/// Named result struct for post + author username.
#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct PostRow {
    pub id: i64,
    pub title: String,
    pub body: String,
    pub created_time: String,
    pub author_id: i64,
    pub category: String,
    pub author_username: String,
}

// ── Schedule ─────────────────────────────────────────────────────────────────

#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct ScheduleItem {
    pub id: i64,
    pub name: String,
    pub description: String,
    pub start_time: String,
    pub end_time: String,
    pub event_id: i64,
}

// ── SeatMap ──────────────────────────────────────────────────────────────────

#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct SeatMap {
    pub id: i64,
    pub event_id: i64,
    pub seat_size: i64,
}

#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct Seat {
    pub id: i64,
    pub seatmap_id: i64,
    pub x: i64,
    pub y: i64,
    pub status: String,
    pub participant_id: Option<i64>,
}

#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct SeatTable {
    pub id: i64,
    pub seatmap_id: i64,
    pub x: i64,
    pub y: i64,
    pub w: i64,
    pub h: i64,
    pub name: String,
}

// ── Sponsorship ──────────────────────────────────────────────────────────────

#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct Sponsor {
    pub id: i64,
    pub name: String,
    pub contact_name: String,
    pub contact_email: String,
    pub contact_phone: String,
    pub lan_rep_id: Option<i64>,
    pub notes: String,
    pub contact_form_url: String,
    pub banner_url: String,
    pub banner_path: Option<String>,
    pub featured_sponsor: i64,
    pub featured_banner_path: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct EventSponsor {
    pub id: i64,
    pub sponsor_id: i64,
    pub event_id: i64,
    pub status: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct Prize {
    pub id: i64,
    pub event_sponsor_id: i64,
    pub name: String,
    pub description: String,
    pub raffle_prize: i64,
}

// ── Tournaments ──────────────────────────────────────────────────────────────

#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct Game {
    pub id: i64,
    pub name: String,
    pub platform: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct Tournament {
    pub id: i64,
    pub name: String,
    pub game_id: i64,
    pub event_id: i64,
    pub team_size: i64,
    pub max_teams: i64,
    pub rules: Option<String>,
    pub html_rules: Option<String>,
    pub style: String,
    pub slugified_name: String,
    pub is_active: i64,
    pub has_started: i64,
}

impl Tournament {
    pub fn style_display(&self) -> &'static str {
        match self.style.as_str() {
            "S" => "Single Elimination",
            "D" => "Double Elimination",
            "R" => "Round Robin",
            "W" => "Swiss",
            _ => "Unknown",
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct Team {
    pub id: i64,
    pub name: String,
    pub password: String,
    pub tournament_id: i64,
    pub owner_id: i64,
}

/// Named result for tournament listing with team count.
#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct TournamentListRow {
    pub id: i64,
    pub name: String,
    pub max_teams: i64,
    pub team_count: i64,
}

/// Named result for team listing with member count and owner.
#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct TeamListRow {
    pub id: i64,
    pub name: String,
    pub tournament_id: i64,
    pub owner_id: i64,
    pub member_count: i64,
    pub owner_username: String,
}

/// Named result for team members list.
#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct MemberRow {
    pub username: String,
}

// ── Carpool ──────────────────────────────────────────────────────────────────

#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct CarpoolOffer {
    pub id: i64,
    pub driver_id: i64,
    pub event_id: i64,
    pub origin_city: String,
    pub origin_state: String,
    pub total_seats: i64,
    pub notes: String,
    pub contact_email: String,
    pub created_time: String,
}

impl CarpoolOffer {
    pub fn seats_remaining(&self, rider_count: i64) -> i64 {
        self.total_seats - rider_count
    }

    pub fn is_full(&self, rider_count: i64) -> bool {
        self.seats_remaining(rider_count) <= 0
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct CarpoolRider {
    pub id: i64,
    pub rider_id: i64,
    pub offer_id: i64,
    pub joined_time: String,
}

/// Named result for carpool offer listing with driver name and rider count.
#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct CarpoolOfferListRow {
    pub id: i64,
    pub driver_id: i64,
    pub event_id: i64,
    pub origin_city: String,
    pub origin_state: String,
    pub total_seats: i64,
    pub notes: String,
    pub contact_email: String,
    pub created_time: String,
    pub driver_username: String,
    pub rider_count: i64,
}

/// Named result for carpool rider listing with rider username.
#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct CarpoolRiderRow {
    pub username: String,
    pub joined_time: String,
}

