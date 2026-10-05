import streamlit as st


def apply_theme():
    st.markdown(
        """
        <style>

        /* ===== GLOBAL ===== */

        #MainMenu {
            visibility: hidden;
        }

        footer {
            visibility: hidden;
        }

        header {
            background: transparent !important;
        }

        .stApp {
            background: #f7f9fc;
        }

        .block-container {
            max-width: 100%;
            padding: 1.2rem 2rem 2rem 2rem;
        }

        * {
            font-family:
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                sans-serif;
        }


        /* ===== SIDEBAR ===== */

        section[data-testid="stSidebar"] {
            background: linear-gradient(
                180deg,
                #071426 0%,
                #0b1d35 55%,
                #071426 100%
            );

            min-width: 245px;
            max-width: 245px;
        }

        section[data-testid="stSidebar"] > div {
            padding: 1.2rem 0.8rem;
        }

        section[data-testid="stSidebar"] * {
            color: #dce7f7;
        }


        /* ===== BRAND ===== */

        .brand {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 8px 10px 25px 10px;
        }

        .brand-icon {
            width: 38px;
            height: 38px;
            border-radius: 11px;

            display: flex;
            align-items: center;
            justify-content: center;

            background: linear-gradient(
                135deg,
                #ffffff,
                #dbeafe
            );

            color: #1458d9;
            font-size: 20px;
            font-weight: 800;
        }

        .brand-title {
            font-size: 15px;
            font-weight: 800;
            line-height: 1.15;
            color: white;
        }

        .brand-subtitle {
            font-size: 10px;
            color: #8fa5c1;
            margin-top: 3px;
        }


        /* ===== METRIC CARDS ===== */

        div[data-testid="stMetric"] {
            padding: 18px;
            border-radius: 14px;

            background: rgba(255,255,255,0.95);

            border: 1px solid #e2e9f3;

            box-shadow:
                0 5px 18px rgba(15,23,42,0.045);

            min-height: 105px;
        }

        div[data-testid="stMetricLabel"] {
            font-size: 11px !important;
            color: #718096 !important;
        }

        div[data-testid="stMetricValue"] {
            color: #172554 !important;
            font-size: 25px !important;
            font-weight: 800 !important;
        }


        /* ===== BUTTONS ===== */

        .stButton > button {
            border-radius: 9px;

            border: 1px solid #dbe4f0;

            background: white;

            color: #1e40af;

            font-weight: 650;

            min-height: 38px;
        }

        .stButton > button:hover {
            border-color: #2563eb;
            color: #2563eb;
        }


        /* ===== INPUTS ===== */

        .stTextInput input,
        .stSelectbox div[data-baseweb="select"],
        .stDateInput input {
            border-radius: 9px !important;
            border-color: #dce4ef !important;
            background: white !important;
        }


        /* ===== FILE UPLOADER ===== */

        section[data-testid="stFileUploaderDropzone"] {
            border: 1.5px dashed #60a5fa !important;

            border-radius: 13px !important;

            background: #ffffff !important;

            min-height: 180px;
        }


        /* ===== TABLE ===== */

        div[data-testid="stDataFrame"] {
            border-radius: 12px;
            border: 1px solid #e0e7f0;
            overflow: hidden;
        }


        /* ===== ALERTS ===== */

        div[data-testid="stAlert"] {
            border-radius: 10px;
            border-width: 1px;
        }


        /* ===== EXPANDERS ===== */

        div[data-testid="stExpander"] {
            border-radius: 10px !important;
            border: 1px solid #e1e8f1 !important;
            background: white;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


def render_brand():
    st.sidebar.markdown(
        """
        <div class="brand">

            <div class="brand-icon">
                ◈
            </div>

            <div>
                <div class="brand-title">
                    PayFlow<br>Intelligence
                </div>

                <div class="brand-subtitle">
                    Smarter Payments. Cleaner Data.
                </div>
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


def render_backend_status():
    st.sidebar.markdown(
        """
        <div style="
            margin: 22px 6px 5px 6px;
            padding: 12px;
            border: 1px solid rgba(255,255,255,0.12);
            border-radius: 10px;
            background: rgba(255,255,255,0.035);
            font-size: 11px;
        ">
            <span style="
                display:inline-block;
                width:8px;
                height:8px;
                border-radius:50%;
                background:#31d17c;
                margin-right:7px;
            "></span>

            <b>Backend Status</b>

            <br>

            <span style="
                margin-left:15px;
                color:#7f95b1;
            ">
                FastAPI Connected
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_page_header(title, subtitle):
    st.markdown(
        f"""
        <div style="
            font-size:28px;
            font-weight:800;
            color:#102044;
            margin-bottom:3px;
        ">
            {title}
        </div>

        <div style="
            color:#748197;
            font-size:12px;
            margin-bottom:25px;
        ">
            {subtitle}
        </div>
        """,
        unsafe_allow_html=True,
    )
