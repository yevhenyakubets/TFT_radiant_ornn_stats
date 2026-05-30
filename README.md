# TFT_radiant_ornn_stats

<a id="readme-top"></a>

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![LinkedIn][linkedin-shield]][linkedin-url]

<br />
<div align="center">
  <a href="https://github.com/github_username/tft-radiant-ornn-stats">
    <!-- TODO: Add a logo/screenshot here -->
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">TFT Radiant & Artifact Stats</h3>

  <p align="center">
    A statistics tracker for Teamfight Tactics that shows which radiant items and artifacts perform best on which champions — relative to each champion's baseline performance across high-ELO EUW games.
    <br />
    <br />
    <a href="https://github.com/github_username/tft-radiant-ornn-stats/issues/new?labels=bug">Report Bug</a>
    &middot;
    <a href="https://github.com/github_username/tft-radiant-ornn-stats/issues/new?labels=enhancement">Request Feature</a>
  </p>
</div>

---

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#about-the-project">About The Project</a></li>
    <li><a href="#built-with">Built With</a></li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#data-pipeline">Data Pipeline</a></li>
    <li><a href="#disclaimer">Disclaimer</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>

---

## About The Project

<!-- TODO: Replace with a real screenshot or GIF once hosted -->
[![Product Screenshot][product-screenshot]](https://example.com)

Most TFT stat sites show average placement, but that metric alone favors lower-cost champions who naturally place better. This project introduces **delta** — the difference between a champion's average placement with a specific item versus their overall average placement. A negative delta means the item improves the champion's performance relative to their baseline.

**Key features:**
- Per-item stats: average placement and delta for every champion that uses it
- Per-champion stats: average placement and delta for every artifact and radiant item
- Hover tooltips showing champion ability descriptions and item stats
- Searchable champion and item list pages (search by name or `#trait`)
- Data sourced from high-ELO EUW games and updated automatically via a scheduled pipeline

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## Built With

* [![React][React.js]][React-url]
* [![Vite][Vite-badge]][Vite-url]
* [![FastAPI][FastAPI-badge]][FastAPI-url]
* [![PostgreSQL][Postgres-badge]][Postgres-url]
* [![Docker][Docker-badge]][Docker-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker + Docker Compose
- A Riot Games API key (set in `.env`)

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/github_username/tft-radiant-ornn-stats.git
   cd tft-radiant-ornn-stats
   ```

2. Set up environment variables
   ```sh
   cp .env.example .env
   # Fill in DATABASE_URL, RIOT_API_KEY, DB_USER, DB_PASSWORD, DB_NAME
   ```

3. Start the database
   ```sh
   docker compose up -d
   ```

4. Set up the backend
   ```sh
   cd backend
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   # source .venv/bin/activate  # Linux/Mac
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

5. Set up the frontend
   ```sh
   cd frontend
   npm install
   npm run dev
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## Data Pipeline

Match data is fetched from the Riot Games API and processed in stages. Run the full pipeline with:

```sh
python -m app.scripts.riot_ingest --tier diamond --division I
python -m app.scripts.riot_ingest --tier diamond --division II
python -m app.scripts.riot_ingest --tier diamond --division III
python -m app.scripts.riot_ingest --tier diamond --division IV
python -m app.scripts.riot_ingest --tier master
python -m app.scripts.riot_ingest --tier grandmaster
python -m app.scripts.riot_ingest --tier challenger
python -m app.scripts.populate_champion_stats_table
python -m app.scripts.populate_champion_item_stats_table
python -m app.scripts.db_cleanup
```

The pipeline is scheduled to run automatically via Windows Task Scheduler. Raw match data is stored temporarily and cleaned up after processing — only the aggregated stats tables are kept long-term.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## Disclaimer

This site isn't endorsed by Riot Games and doesn't reflect the views or opinions of Riot Games or anyone officially involved in producing or managing Riot Games properties. Riot Games, and all associated properties are trademarks or registered trademarks of Riot Games, Inc.

Data powered by the Riot Games API.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## Contact

<!-- TODO: Fill in your details -->
Yevhen Yakubets - [LinkedIn](https://linkedin.com/in/linkedin_username) - yevhen.yakubets@gmail.com

Project Link: [https://github.com/github_username/tft-radiant-ornn-stats](https://github.com/github_username/tft-radiant-ornn-stats)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

<!-- MARKDOWN LINKS & IMAGES -->
[contributors-shield]: https://img.shields.io/github/contributors/github_username/tft-radiant-ornn-stats.svg?style=for-the-badge
[contributors-url]: https://github.com/github_username/tft-radiant-ornn-stats/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/github_username/tft-radiant-ornn-stats.svg?style=for-the-badge
[forks-url]: https://github.com/github_username/tft-radiant-ornn-stats/network/members
[stars-shield]: https://img.shields.io/github/stars/github_username/tft-radiant-ornn-stats.svg?style=for-the-badge
[stars-url]: https://github.com/github_username/tft-radiant-ornn-stats/stargazers
[issues-shield]: https://img.shields.io/github/issues/github_username/tft-radiant-ornn-stats.svg?style=for-the-badge
[issues-url]: https://github.com/github_username/tft-radiant-ornn-stats/issues
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/linkedin_username
[product-screenshot]: images/screenshot.png

[React.js]: https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB
[React-url]: https://reactjs.org/
[Vite-badge]: https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white
[Vite-url]: https://vitejs.dev/
[FastAPI-badge]: https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white
[FastAPI-url]: https://fastapi.tiangolo.com/
[Postgres-badge]: https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white
[Postgres-url]: https://www.postgresql.org/
[Docker-badge]: https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white
[Docker-url]: https://www.docker.com/