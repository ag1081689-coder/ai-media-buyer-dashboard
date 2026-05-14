# AI Media Buyer Dashboard

## Features
- Connect to Meta Ads Manager API
- Export campaigns data to CSV
- Analyze campaigns performance
- Streamlit dashboard

## Setup

### 1. Install requirements

```bash
pip install -r requirements.txt
```

### 2. Configure environment variables

Rename `.env.example` to `.env`

Add:

```env
META_ACCESS_TOKEN=your_token
META_AD_ACCOUNT_ID=act_your_account_id
```

### 3. Run data fetcher

```bash
python meta_ads_fetcher.py
```

### 4. Run dashboard

```bash
streamlit run dashboard.py
```
