# HoodSafe.org – SEO Growth Strategy

*Planning docs from Corppu (Mar 6, 2026)*

## Goal
Scale to 500K-2M+ monthly visitors via programmatic SEO.

---

## 1. Data Sources

### Core (Free)
- **FBI Crime Data Explorer** (UCR/NIBRS): ~16,000 agencies, 94-96% US coverage
- **Census Bureau**: Population data for per-capita rates (crimes per 1,000)
- **Census TIGER**: Geographic boundaries
- **Local Police Portals**: Incident-level data with coordinates (what we have now for 16 cities)

### Optional (Paid)
- **Crimeometer API**: Real-time incident feeds, "crimes near you" features

---

## 2. Scale Potential 🚀

| Page Type | Count | Example URL |
|-----------|-------|-------------|
| City pages | ~19,000 | `/city/chicago-crime-rate` |
| County pages | ~3,143 | `/county/los-angeles-county-crime-rate` |
| Comparison pages | ~125,000 | `/compare/chicago-vs-austin-crime` |
| Ranking pages | ~500 | `/safest-cities-in-california` |
| ZIP code pages | ~33,000 | `/zip/60601-crime-rate` |
| **TOTAL** | **150,000+** | |

**Traffic Potential:**
- Year 1: 50K-200K monthly visitors
- Long term: 500K-2M+ monthly visitors

---

## 3. Safety Score Formula

| Component | Weight |
|-----------|--------|
| Violent crime rate | 50% |
| Property crime rate | 30% |
| Trend (improving/worsening) | 20% |

Score: 0-100 (higher = safer)

---

## 4. Page Content Requirements

Each page must include (to avoid thin content):
- ✅ Crime statistics (violent, property, total)
- ✅ Population context
- ✅ Safety score (0-100)
- ✅ Trend charts (multi-year)
- ✅ Comparison to national average
- ✅ Nearby city comparisons
- ✅ Schema.org markup

---

## 5. Competitive Advantage

### Multilingual SEO 🌍
Most crime sites are English-only. Translate key pages to:
- Spanish, German, French, Chinese, Japanese
- Target expats researching US cities

---

## 6. Build Phases

### Phase 1: City Pages (Current)
- `/city/{city}-crime-rate` for 500 largest cities
- FBI UCR data + Census population
- Template: score, stats, chart, nearby comparisons

### Phase 2: Comparison Engine
- `/compare/{city1}-vs-{city2}-crime`
- Auto-generate for top 500 cities (125K pages)
- Show score difference, stat breakdown

### Phase 3: Rankings
- `/safest-cities-in-{state}` (50 states)
- `/most-dangerous-cities-in-america`
- Attract backlinks & media

### Phase 4: Counties
- `/county/{county}-crime-rate`
- 3,143 counties with FBI data

### Phase 5: ZIP Codes
- `/zip/{zipcode}-crime-rate`
- 33,000 ZIP codes for deep coverage

### Phase 6: Multilingual
- Translate top 1000 pages
- 5 languages = 5000 additional pages
