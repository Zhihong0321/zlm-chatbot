-- Add missing columns to chat_messages table
ALTER TABLE chat_messages ADD COLUMN IF NOT EXISTS tools_used JSON;
ALTER TABLE chat_messages ADD COLUMN IF NOT EXISTS mcp_server_responses JSON;

-- Verify the changes
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'chat_messages' 
AND table_schema = 'public'
ORDER BY ordinal_position;
