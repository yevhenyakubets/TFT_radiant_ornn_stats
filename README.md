# TFT_radiant_ornn_stats

<a id="readme-top"></a>

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![LinkedIn][linkedin-shield]][linkedin-url]

<br />
<div align="center">
  <a href="https://github.com/yevhenyakubets/TFT_radiant_ornn_stats">
    <!-- TODO: Add a logo/screenshot here -->
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">TFT Boris</h3>

  <p align="center">
    A personal web project focused analyzing statistics for the game Teamfight Tactics in order to find the best items for a champion, or find the best users of a specific item 
    <br />
    <a href="https://github.com/yevhenyakubets/TFT_radiant_ornn_stats/issues/new?labels=bug">Report Bug</a>
    &middot;
    <a href="https://github.com/yevhenyakubets/TFT_radiant_ornn_stats/issues/new?labels=enhancement">Request Feature</a>
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

This project delivers the core functionality of a TFT stats website, specializing specifically in Artifacts and Radiant items. Every champion and item has a dedicated page displaying average placements alongside relative average placement (delta). The underlying data is constantly updated and processed by tapping directly into the Riot API.

While the primary goal of this project was to gain hands-on experience with APIs, FastAPI, databases, React, and full-stack web development, I also aimed to build a highly practical, clean, and visually appealing website.

**Key features:**

**-Automated Data Pipeline**: Background tasks powered by Celery and Redis continuously fetch, process, and update champion statistics directly from the Riot API without blocking user traffic.

**-Per-Item Stats**: Average placement and delta metrics for every champion that utilizes the item.

**-Per-Champion Stats**: Detailed breakdown of average placement and delta for all eligible Artifacts and Radiant items.

**-Interactive UI**: Hover tooltips for quick item/champion references and fully parsed, readable descriptions of all items and abilities with all of the numbers.

**-Mobile-Friendly Layout**: Features custom responsive overrides so you can easily check item and champion stats on your phone.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## Built With

* [![React][React.js]][React-url]
* [![Vite][Vite-badge]][Vite-url]
* [![FastAPI][FastAPI-badge]][FastAPI-url]
* [![PostgreSQL][Postgres-badge]][Postgres-url]
* [![Redis][Docker-badge]][Docker-url]
* [![Docker Compose][Docker-badge]][Docker-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## Getting Started

> 💡 **Important:** This project and its installation commands are designed to be run in a **Linux** or **Windows Subsystem for Linux (WSL)** terminal environment.

### Prerequisites

- Docker + Docker Compose
- Node.js 18+
- Python 3.14+ (only if running the backend outside Docker)
- A Riot Games API key(you can get one for free)
- Git
- GNU Make

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/yevhenyakubets/TFT_radiant_ornn_stats.git
   cd TFT_radiant_ornn_stats
   ```

2. Copy the environment file and fill in values
   ```sh
   cp .env.example .env
   ```
   Then update `.env` with:
   - `RIOT_API_KEY` (you can get one for free [here](https://developer.riotgames.com/), but it expires after 24 hours)
   - `DB_USER`, `DB_PASSWORD` and `DB_NAME` with whatever you like

   To edit the .env file, use
    ```sh
   nano .env
   ```

3. Start services with Docker Compose
   ```sh
   docker compose up -d
   ```

4. Database migrations
   ```sh
    docker compose exec api uv run alembic upgrade head
   ```

5. Run database sync once manually
  (to populate the database with initial info (items, champions, traits), we need to run this script manually once.)
   ```sh
    docker compose exec api uv run python -m app.scripts.db_sync
   ```

6. Run the frontend container using Make
   ```sh
    make frontend
   ```

7. Open the app
   - Frontend: `http://127.0.0.1:5173`
   - Backend API: `http://127.0.0.1:8000`
   - Flower: `http://127.0.0.1:5555`

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

Project Link: [https://github.com/yevhenyakubets/TFT_radiant_ornn_stats](https://github.com/yevhenyakubets/TFT_radiant_ornn_stats)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

<!-- MARKDOWN LINKS & IMAGES -->
[contributors-shield]: https://img.shields.io/github/contributors/yevhenyakubets/TFT_radiant_ornn_stats.svg?style=for-the-badge
[contributors-url]: https://github.com/yevhenyakubets/TFT_radiant_ornn_stats/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/yevhenyakubets/TFT_radiant_ornn_stats.svg?style=for-the-badge
[forks-url]: https://github.com/yevhenyakubets/TFT_radiant_ornn_stats/network/members
[stars-shield]: https://img.shields.io/github/stars/yevhenyakubets/TFT_radiant_ornn_stats.svg?style=for-the-badge
[stars-url]: https://github.com/yevhenyakubets/TFT_radiant_ornn_stats/stargazers
[issues-shield]: https://img.shields.io/github/issues/yevhenyakubets/TFT_radiant_ornn_stats.svg?style=for-the-badge
[issues-url]: https://github.com/yevhenyakubets/TFT_radiant_ornn_stats/issues
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