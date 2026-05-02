CREATE TABLE IF NOT EXISTS observations (
    id          SERIAL PRIMARY KEY,
    recorded_at TIMESTAMP NOT NULL,
    parameter   VARCHAR(20) NOT NULL,
    aqi         INTEGER NOT NULL,
    category    VARCHAR(50),
    latitude    NUMERIC(9,6),
    longitude   NUMERIC(9,6),
    reporting_area VARCHAR(100),
    state_code  VARCHAR(5)
);

CREATE INDEX IF NOT EXISTS idx_observations_recorded_at ON observations(recorded_at);
CREATE INDEX IF NOT EXISTS idx_observations_parameter ON observations(parameter);
