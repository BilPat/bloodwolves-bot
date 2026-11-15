import sys, json; import os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import news
FOREVER = """<rss><channel><title>Wowhead Blue Tracker</title>
<item><description>At about 20:05 CET today, we deployed a hotfix that increased kill experience in dungeons by 50%...&lt;br&gt;&lt;br&gt;By&lt;a href="https://www.wowhead.com/forever/blue-tracker/author/Kaivax"&gt;Kaivax&lt;/a&gt; on 2026/11/08 at 1:48 PM</description><title>Dungeon Enemy XP Increased - 8 November</title><link>https://www.wowhead.com/forever/blue-tracker/topic/eu/640598</link><pubDate>Sun, 08 Nov 2026 13:48:33 -0600</pubDate></item>
<item><description>At about 11:05 PST today, we deployed a hotfix that increased kill experience in dungeons by 50%...&lt;br&gt;&lt;br&gt;By&lt;a href="https://www.wowhead.com/forever/blue-tracker/author/Kaivax"&gt;Kaivax&lt;/a&gt; on 2026/11/08 at 1:48 PM</description><title>Dungeon Enemy XP Increased - November 8</title><link>https://www.wowhead.com/forever/blue-tracker/topic/us/2406595</link><pubDate>Sun, 08 Nov 2026 13:48:02 -0600</pubDate></item>
<item><description>Thanks for the report, we are looking into it.&lt;br&gt;&lt;br&gt;By&lt;a href="x"&gt;Kaivax&lt;/a&gt; on 2026/11/07</description><title>This is nothing like classic</title><link>https://www.wowhead.com/forever/blue-tracker/topic/us/2406000</link><pubDate>Sat, 07 Nov 2026 10:00:00 -0600</pubDate></item>
<item><description>Here you will find a list of hotfixes...&lt;br&gt;&lt;br&gt;By&lt;a href="y"&gt;Blizzard Entertainment&lt;/a&gt; on 2026/11/06 at 7:16 PM</description><title>WoW: Forever Hotfixes - November 6, 2026 — World of Warcraft — Blizzard News</title><link>https://www.wowhead.com/forever/blue-tracker/news/us/24315281</link><pubDate>Fri, 06 Nov 2026 19:16:01 -0600</pubDate></item>
<item><description>Here you will find a list of hotfixes...&lt;br&gt;&lt;br&gt;By&lt;a href="y"&gt;Blizzard Entertainment&lt;/a&gt; on 2026/11/06 at 7:14 PM</description><title>WoW: Forever Hotfixes - November 6, 2026 — World of Warcraft — Blizzard News</title><link>https://www.wowhead.com/forever/blue-tracker/news/eu/24315281</link><pubDate>Fri, 06 Nov 2026 19:14:04 -0600</pubDate></item>
<item><description>Old post&lt;br&gt;&lt;br&gt;By&lt;a href="y"&gt;Kaivax&lt;/a&gt; on 2026/11/04</description><title>Realm Status Update - November 4</title><link>https://www.wowhead.com/forever/blue-tracker/topic/us/2400000</link><pubDate>Wed, 04 Nov 2026 12:00:00 -0600</pubDate></item>
</channel></rss>"""
FORUM = """<rss><channel><item><title>Dungeon Enemy XP Increased - November 8</title><dc:creator><![CDATA[@Kaivax Kaivax]]></dc:creator><description><![CDATA[ <p>At about 11:05 PST today, we deployed a hotfix that increased kill experience in dungeons by 50%, so it feels better to go back in for more runs.</p> <p>Happy dungeon crawling, and good luck with those <strong>Deviate Hides</strong>!</p> <ul><li>one</li><li>two</li></ul> ]]></description><link>https://us.forums.blizzard.com/en/wow/t/dungeon-enemy-xp-increased-november-8/2406595/1</link></item></channel></rss>"""
def fetcher(url): return FOREVER if "wowhead" in url else FORUM
# first run: only newest 3 groups post, the rest are recorded quietly
state = {}
embeds, state = news.build_news(state, now_ts=1_794_200_000, fetcher=fetcher)
titles = [e["title"] for e in embeds]
print(json.dumps(embeds, indent=1, ensure_ascii=False))
assert titles == ["WoW: Forever Hotfixes - November 6, 2026", "Dungeon Enemy XP Increased - November 8"], titles  # "nothing like classic" skipped as a short reply
assert embeds[0]["url"] == "https://news.blizzard.com/en-us/article/24315281"
assert embeds[1]["url"] == "https://us.forums.blizzard.com/en/wow/t/2406595"
assert "**Deviate Hides**" in embeds[1]["description"] and "• one" in embeds[1]["description"]
assert embeds[1]["footer"]["text"] == "Hotfixes · Kaivax · US forums"
assert news.norm_title("Realm Status Update - November 4") in state["news_seen"]
# second run: nothing new
embeds2, state = news.build_news(state, now_ts=1_794_200_600, fetcher=fetcher)
assert embeds2 == [], embeds2
# feed down: no crash, no posts
embeds3, _ = news.build_news(state, fetcher=lambda u: (_ for _ in ()).throw(OSError("down")))
assert embeds3 == []
# promotional titles are skipped, real notices are kept
assert news.is_promo("Watch the WoW: Forever Podcast – The Lore Episode")
assert news.is_promo("WoW Weekly Highlights the WoW: Forever Podcast, a New Short Story, This Week’s Videos, and More!")
assert not news.is_promo("Lost Training Purchase Refunds - November 13")
assert not news.is_promo("Hotfixes: November 13, 2026")
# US/EU twins with different dates in the title post once
def _feed(items):
    rows = "".join(f"<item><title>{t}</title><link>https://www.wowhead.com/forever/blue-tracker/topic/{r}/{i}</link><description>{"Body text long enough to be a real notice. " * 8}</description><pubDate>Sat, 14 Nov 2026 1{i}:00:00 GMT</pubDate></item>" for i, (t, r) in enumerate(items))
    return f"<rss><channel>{rows}</channel></rss>"
st = {"news_seen": {"x": 1}, "news_started": True}
feed1 = _feed([("Player-Level Dungeon XP Adjustment - November 14", "us")])
e1, st = news.build_news(st, now_ts=1794700000, fetcher=lambda u: feed1 if "blue-tracker" in u else "<rss><channel></channel></rss>")
feed2 = _feed([("Player-Level Dungeon XP Adjustment - November 14", "us"), ("Player-Level Dungeon XP Adjustment - 15 November", "eu")])
e2, st = news.build_news(st, now_ts=1794700000 + 3600, fetcher=lambda u: feed2 if "blue-tracker" in u else "<rss><channel></channel></rss>")
assert len(e1) == 1 and len(e2) == 0, (len(e1), len(e2))
print("news tests pass")
