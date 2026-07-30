BEGIN;

-- Running upgrade 3790329c5718 -> a71f0dbc3301

ALTER TABLE conversations ADD COLUMN user_id UUID;

DO $$
        DECLARE
            legacy_conversation_count BIGINT;
            default_user_id UUID;
        BEGIN
            SELECT COUNT(*)
            INTO legacy_conversation_count
            FROM conversations
            WHERE user_id IS NULL;

            IF legacy_conversation_count > 0 THEN
                SELECT id
                INTO default_user_id
                FROM users
                ORDER BY created_at ASC, id ASC
                LIMIT 1;

                IF default_user_id IS NULL THEN
                    RAISE EXCEPTION
                        'Cannot migrate existing conversations because '
                        'the users table contains no users.';
                END IF;

                UPDATE conversations
                SET user_id = default_user_id
                WHERE user_id IS NULL;
            END IF;
        END
        $$;;

ALTER TABLE conversations ALTER COLUMN user_id SET NOT NULL;

ALTER TABLE conversations ADD CONSTRAINT fk_conversations_user_id_users FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE;

CREATE INDEX ix_conversations_user_id ON conversations (user_id);

UPDATE alembic_version SET version_num='a71f0dbc3301' WHERE alembic_version.version_num = '3790329c5718';

COMMIT;

