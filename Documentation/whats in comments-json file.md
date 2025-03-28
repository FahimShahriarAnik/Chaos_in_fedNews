| Field | Type | Description | Relevance to FedNews Analysis |
|-------|------|-------------|-------------------------------|
| `_meta` | Object | Metadata about data retrieval | ❌ Technical only |
| `_meta.retrieved_2nd_on` | Integer | Unix timestamp when data was retrieved | ❌ Technical only |
| `all_awardings` | Array | Awards given to post (empty = none) | ❌ Rarely used |
| `approved_at_utc` | Integer | When post was approved by mods (null = not approved) | ⚠️ Moderation insight |
| `approved_by` | String | Moderator who approved post | ⚠️ Moderation insight |
| `archived` | Boolean | Whether post is archived | ❌ Low value |
| `associated_award` | Null | Legacy field (unused) | ❌ Ignore |
| `author` | String | Username of post author | ✅ Track user activity |
| `author_flair_*` | Mixed | User flair styling (colors, text) | ⚠️ Potential role indicator |
| `author_fullname` | String | Reddit internal user ID (t2_xxxx) | ❌ Technical only |
| `author_is_blocked` | Boolean | If author is blocked by you | ❌ Personal setting |
| `author_patreon_flair` | Boolean | Patreon supporter badge | ❌ Irrelevant |
| `author_premium` | Boolean | Reddit Premium status | ❌ Irrelevant |
| `awarders` | Array | Users who gave awards | ❌ Low value |
| `banned_at_utc` | Integer | When author was banned | ⚠️ Moderation insight |
| `banned_by` | String | Mod who banned author | ⚠️ Moderation insight |
| `body` | String | Comment text content | ✅ Primary analysis target |
| `can_gild` | Boolean | If post can receive awards | ❌ Irrelevant |
| `can_mod_post` | Boolean | If user can mod | ❌ Permission flag |
| `collapsed*` | Mixed | Comment collapse status | ❌ UI feature |
| `comment_type` | Null | Legacy field | ❌ Ignore |
| `controversiality` | Integer | Controversy score (0 = not controversial) | ✅ Engagement metric |
| `created` | Integer | Post creation timestamp (local) | ✅ Time-series analysis |
| `created_utc` | Integer | Post creation timestamp (UTC) | ✅ Time-series analysis |
| `distinguished` | Null | Mod/admin distinction | ⚠️ Moderation insight |
| `downs` | Integer | Downvotes (deprecated) | ❌ Always 0 |
| `edited` | Boolean/Integer | Edit status/timestamp | ⚠️ Content changes |
| `gilded` | Integer | Award count | ❌ Deprecated |
| `gildings` | Object | Award details | ❌ Low value |
| `id` | String | Unique post ID | ✅ Reference key |
| `is_submitter` | Boolean | If author is OP | ⚠️ Conversation role |
| `likes` | Null | Vote direction (null = no vote) | ❌ User-specific |
| `link_id` | String | Parent post ID | ✅ Thread mapping |
| `locked` | Boolean | If post is locked | ⚠️ Moderation insight |
| `mod_note` | Null | Mod notes | ⚠️ Moderation insight |
| `mod_reason_*` | Null | Mod action reasons | ⚠️ Moderation insight |
| `mod_reports` | Array | Mod reports | ⚠️ Controversy flag |
| `name` | String | Full ID (t1_xxxx) | ❌ Technical |
| `no_follow` | Boolean | SEO attribute | ❌ Irrelevant |
| `num_reports` | Integer | User reports count | ✅ Controversy metric |
| `parent_id` | String | Parent comment ID | ✅ Thread structure |
| `permalink` | String | URL to comment | ✅ Reference |
| `removal_reason` | Null | Removal reason | ⚠️ Moderation insight |
| `replies` | String | Child comments (empty in your data) | ✅ Conversation depth |
| `report_reasons` | Null | Report types | ⚠️ Moderation insight |
| `retrieved_on` | Integer | Data scrape timestamp | ❌ Technical |
| `saved` | Boolean | If you saved post | ❌ Personal |
| `score` | Integer | Net votes (ups - downs) | ✅ Engagement metric |
| `score_hidden` | Boolean | If score is hidden | ❌ UI feature |
| `send_replies` | Boolean | If OP gets reply notifications | ❌ User setting |
| `stickied` | Boolean | If post is pinned | ⚠️ Importance flag |
| `subreddit` | String | Subreddit name | ✅ Filter |
| `subreddit_id` | String | Subreddit ID | ❌ Technical |
| `subreddit_name_prefixed` | String | "r/fednews" | ❌ Redundant |
| `subreddit_type` | String | "public" | ❌ Constant |
| `top_awarded_type` | Null | Legacy field | ❌ Ignore |
| `total_awards_received` | Integer | Award count | ❌ Low value |
| `treatment_tags` | Array | Reddit experiment flags | ❌ Internal use |
| `unrepliable_reason` | Null | Why replies disabled | ⚠️ Moderation |
| `ups` | Integer | Upvotes (deprecated) | ❌ Use `score` |
| `user_reports` | Array | User reports | ⚠️ Controversy |