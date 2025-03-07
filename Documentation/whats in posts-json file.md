File Structure:

The JSON file contains multiple Reddit posts, with each post represented as a separate JSON object (one per line).

The file is not a single JSON array, so it needs to be processed line by line.

each field of an object explained.
# Reddit Post JSON Field Descriptions

| Field | Type/Value | Description |
|-------|------------|-------------|
| **`_meta`** | Object | Metadata about data retrieval. |
| → `retrieved_2nd_on` | `1735819500` | Timestamp (Unix epoch) indicating when this data was retrieved/updated. |
| **`all_awardings`** | `[]` | Awards given to the post (empty = no awards). |
| **`allow_live_comments`** | `false` | Whether live commenting is enabled (rarely used). |
| **`approved_at_utc`** | `null` | Timestamp when the post was approved by moderators (`null` = not approved). |
| **`approved_by`** | `null` | Moderator username who approved the post (`null` = not approved). |
| **`archived`** | `false` | Whether the post is archived (no new comments allowed). |
| **`author`** | `"WarcockMountainMan"` | Username of the post's author. |
| **`author_flair_background_color`** | `null` | CSS color code for author's flair background (`null` = none). |
| **`author_flair_css_class`** | `null` | CSS class for author's flair styling (`null` = none). |
| **`author_flair_richtext`** | `[]` | Flair text formatting (empty = no special flair). |
| **`author_flair_template_id`** | `null` | ID for a predefined flair template (`null` = none). |
| **`author_flair_text`** | `null` | Text displayed in the author's flair (`null` = none). |
| **`author_flair_text_color`** | `null` | CSS color code for flair text (`null` = default). |
| **`author_flair_type`** | `"text"` | Type of author flair (e.g., `"text"`, `"richtext"`). |
| **`author_fullname`** | `"t2_5gjx0o9u"` | Reddit's internal user ID (format: `t2_XXXXX`). |
| **`author_is_blocked`** | `false` | Whether the author is blocked by the logged-in user. |
| **`author_patreon_flair`** | `false` | Whether the author has Patreon-linked flair. |
| **`author_premium`** | `false` | Whether the author has Reddit Premium. |
| **`awarders`** | `[]` | List of users who awarded the post (empty = no awards). |
| **`banned_at_utc`** | `null` | Timestamp when the author was banned (`null` = not banned). |
| **`banned_by`** | `null` | Moderator who banned the author (`null` = not banned). |
| **`can_gild`** | `false` | Whether the post can receive awards (gilding). |
| **`can_mod_post`** | `false` | Whether the logged-in user can moderate this post. |
| **`category`** | `null` | Post category (`null` = uncategorized). |
| **`clicked`** | `false` | Whether the logged-in user clicked on the post. |
| **`content_categories`** | `null` | Reddit's content categories (`null` = unspecified). |
| **`contest_mode`** | `false` | Whether contest mode is enabled (randomizes comment order). |
| **`created`** | `1735689878` | Timestamp (Unix epoch) of post creation (local time). |
| **`created_utc`** | `1735689878` | Timestamp (Unix epoch) of post creation (UTC). |
| **`discussion_type`** | `null` | Type of discussion (`null` = default). |
| **`distinguished`** | `null` | Whether the post is distinguished by a moderator (`null` = no). |
| **`domain`** | `"self.fednews"` | Domain of the post (`"self"` = text post in the subreddit). |
| **`downs`** | `0` | Number of downvotes (deprecated by Reddit, usually `0`). |
| **`edited`** | `false` | Whether the post has been edited. |
| **`gilded`** | `0` | Number of times the post received "gold" awards. |
| **`gildings`** | `{}` | Detailed award counts (empty = no awards). |
| **`hidden`** | `false` | Whether the post is hidden by the logged-in user. |
| **`hide_score`** | `false` | Whether the score is hidden (e.g., in contest mode). |
| **`id`** | `"1hqrcez"` | Unique post ID (Reddit format). |
| **`is_created_from_ads_ui`** | `false` | Whether the post was created via Reddit Ads. |
| **`is_crosspostable`** | `true` | Whether the post can be crossposted. |
| **`is_meta`** | `false` | Whether the post is a meta discussion about the subreddit. |
| **`is_original_content`** | `false` | Whether the post is marked as original content. |
| **`is_reddit_media_domain`** | `false` | Whether the media is hosted on Reddit. |
| **`is_robot_indexable`** | `true` | Whether search engines can index the post. |
| **`is_self`** | `true` | Whether the post is a text post (vs. link/image). |
| **`is_video`** | `false` | Whether the post contains a video. |
| **`likes`** | `null` | Whether the logged-in user upvoted (`null` = no vote). |
| **`link_flair_background_color`** | `"#dadada"` | CSS color code for post flair background. |
| **`link_flair_css_class`** | `""` | CSS class for post flair styling. |
| **`link_flair_richtext`** | Array | Flair text formatting (e.g., text/emoji). |
| → `e` | `"text"` | Element type (`"text"` or `"emoji"`). |
| → `t` | `"Misc Question"` | Flair text content. |
| **`link_flair_template_id`** | `"d79e0052-c26a-11ef-88bd-2a6f4f99449d"` | UUID of the flair template. |
| **`link_flair_text`** | `"Misc Question"` | Flair text displayed on the post. |
| **`link_flair_text_color`** | `"dark"` | CSS color code for flair text. |
| **`link_flair_type`** | `"richtext"` | Flair formatting type (`"text"` or `"richtext"`). |
| **`locked`** | `false` | Whether comments are locked. |
| **`media`** | `null` | Embedded media (`null` = no media). |
| **`media_embed`** | `{}` | Media embed data (empty = none). |
| **`media_only`** | `false` | Whether the post is media-only (e.g., image/gallery). |
| **`mod_note`** | `null` | Moderator note (`null` = none). |
| **`mod_reason_by`** | `null` | Moderator who added a removal reason (`null` = none). |
| **`mod_reason_title`** | `null` | Reason for moderation action (`null` = none). |
| **`mod_reports`** | `[]` | Moderator reports (empty = none). |
| **`name`** | `"t3_1hqrcez"` | Fullname of the post (`t3_` + ID). |
| **`no_follow`** | `false` | Whether links in the post have "nofollow" tags. |
| **`num_comments`** | `8` | Total number of comments. |
| **`num_crossposts`** | `0` | Number of times the post was crossposted. |
| **`num_reports`** | `null` | Number of user reports (`null` = hidden). |
| **`over_18`** | `false` | Whether the post is marked as NSFW. |
| **`permalink`** | `"/r/fednews/comments/1hqrcez/..."` | URL path to the post. |
| **`pinned`** | `false` | Whether the post is pinned in the subreddit. |
| **`pwls`** | `6` | Subreddit "personalization where to list" score (obscure metric). |
| **`quarantine`** | `false` | Whether the subreddit is quarantined. |
| **`removal_reason`** | `null` | Reason for post removal (`null` = not removed). |
| **`removed_by`** | `null` | Moderator who removed the post (`null` = not removed). |
| **`removed_by_category`** | `null` | Category of removal (`null` = not removed). |
| **`report_reasons`** | `null` | Reasons for user reports (`null` = none). |
| **`retrieved_on`** | `1735689899` | Timestamp (Unix epoch) when data was scraped. |
| **`saved`** | `false` | Whether the post is saved by the logged-in user. |
| **`score`** | `0` | Post score (upvotes - downvotes). |
| **`secure_media`** | `null` | Secure media embed (`null` = none). |
| **`secure_media_embed`** | `{}` | Secure media embed data (empty = none). |
| **`selftext`** | `"See title..."` | Body text of the post. |
| **`send_replies`** | `true` | Whether the author receives reply notifications. |
| **`spoiler`** | `false` | Whether the post is marked as a spoiler. |
| **`stickied`** | `false` | Whether the post is stickied (same as "pinned"). |
| **`subreddit`** | `"fednews"` | Subreddit name. |
| **`subreddit_id`** | `"t5_2xy8z"` | Reddit's internal subreddit ID. |
| **`subreddit_name_prefixed`** | `"r/fednews"` | Subreddit name with prefix. |
| **`subreddit_subscribers`** | `124860` | Number of subreddit subscribers. |
| **`subreddit_type`** | `"public"` | Subreddit type (`public`/`private`/`restricted`). |
| **`suggested_sort`** | `"confidence"` | Default comment sorting method. |
| **`thumbnail`** | `"self"` | Thumbnail image type (`"self"` = text post thumbnail). |
| **`thumbnail_height`** | `null` | Thumbnail height (`null` = no thumbnail). |
| **`thumbnail_width`** | `null` | Thumbnail width (`null` = no thumbnail). |
| **`title`** | `"Connecticut feds..."` | Title of the post. |
| **`top_awarded_type`** | `null` | Type of top award (`null` = none). |
| **`total_awards_received`** | `0` | Total number of awards received. |
| **`treatment_tags`** | `[]` | Reddit admin tags (e.g., for A/B tests). |
| **`ups`** | `0` | Upvotes count (deprecated; use `score` instead). |
| **`upvote_ratio`** | `0.2` | Ratio of upvotes to total votes (`0.2` = 20% upvotes). |
| **`url`** | `"https://www.reddit.com/..."` | Full URL to the post. |
| **`user_reports`** | `[]` | User reports (empty = none). |
| **`view_count`** | `null` | View count (`null` = not tracked). |
| **`visited`** | `false` | Whether the logged-in user has viewed the post. |
| **`wls`** | `6` | Whitelist status (obscure subreddit setting). |