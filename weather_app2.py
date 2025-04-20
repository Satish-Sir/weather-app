import sqlite3
import hashlib
import requests
import streamlit as st
import time
from datetime import datetime
from matplotlib import pyplot as plt
from matplotlib import dates

# -------------- CONFIG --------------
st.set_page_config(page_title="Weather Forecast App", layout="centered")

# API Key for WeatherAPI
api_key = "a3c707aeefbc4da2b0425837251003"
sign = u"\N{DEGREE SIGN}"

# Dictionary of states and their respective districts
states_districts = {
    "Andhra Pradesh": [
        "Anantapur", "Chittoor", "East Godavari", "Guntur", "Krishna", "Kurnool", 
        "Prakasam", "Srikakulam", "Visakhapatnam", "West Godavari", "YSR Kadapa"
    ],
    "Bihar": [
        "Araria", "Aurangabad", "Banka", "Begusarai", "Bhagalpur", "Buxar", "Darbhanga", 
        "East Champaran", "Gaya", "Gopalganj", "Jamui", "Jehanabad", "Khagaria", "Kishanganj", 
        "Lakhisarai", "Madhepura", "Madhubani", "Munger", "Muzaffarpur", "Nalanda", "Nawada", 
        "Patna", "Purnia", "Rohtas", "Saharsa", "Samastipur", "Saran", "Sheikhpura", 
        "Sheohar", "Sitamarhi", "Supaul", "Vaishali", "West Champaran"
    ],
    "Karnataka": [
        "Bagalkot", "Bangalore Urban", "Belagavi", "Bellary", "Bidar", "Chamarajanagar", 
        "Chikkamagaluru", "Chitradurga", "Dakshina Kannada", "Davangere", "Gadag", "Hassan", 
        "Haveri", "Kodagu", "Kolar", "Koppal", "Mandya", "Mysuru", "Raichur", "Ramanagara", 
        "Shivamogga", "Tumakuru", "Udupi", "Uttara Kannada", "Vijayapura", "Yadgir"
    ],
    "Maharashtra": [
        "Ahmednagar", "Akola", "Amravati", "Aurangabad", "Bhandara", "Beed", "Buldhana", 
        "Chandrapur", "Dhule", "Gadchiroli", "Gondia", "Hingoli", "Jalna", "Kolhapur", 
        "Latur", "Mumbai City", "Mumbai Suburban", "Nanded", "Nagpur", "Nandurbar", 
        "Nasik", "Osmanabad", "Palghar", "Parbhani", "Pune", "Raigad", "Ratnagiri", 
        "Sangli", "Satara", "Sindhudurg", "Solapur", "Thane", "Wardha", "Washim", 
        "Yavatmal"
    ],
    "Uttar Pradesh": [
        "Agra", "Aligarh", "Allahabad", "Ambedkar Nagar", "Auraiya", "Azamgarh", "Baghpat", 
        "Bahraich", "Ballia", "Balrampur", "Banda", "Barabanki", "Basti", "Bijnor", 
        "Budaun", "Bulandshahr", "Chandauli", "Chitrakoot", "Deoria", "Etah", "Etawah", 
        "Faizabad", "Farrukhabad", "Fatehpur", "Firozabad", "Gautam Buddha Nagar", 
        "Ghaziabad", "Ghazipur", "Gonda", "Hamirpur", "Hardoi", "Hathras", "Jhansi", 
        "Jalaun", "Jaunpur", "Kanpur Dehat", "Kanpur Nagar", "Kasganj", "Kaushambi", 
        "Kushinagar", "Lakhimpur Kheri", "Lalitpur", "Lucknow", "Maharajganj", 
        "Mainpuri", "Mathura", "Mau", "Meerut", "Mirzapur", "Moradabad", "Muzaffarnagar", 
        "Pilibhit", "Pratapgarh", "Rae Bareli", "Rampur", "Saharanpur", "Sambhal", 
        "Sant Kabir Nagar", "Shahjahanpur", "Shamli", "Siddharth Nagar", "Sitapur", 
        "Sonbhadra", "Sultanpur", "Unnao", "Varanasi"
    ],
    "Tamil Nadu": [
        "Ariyalur", "Chengalpattu", "Chennai", "Coimbatore", "Cuddalore", "Dharmapuri", 
        "Dindigul", "Erode", "Kallakurichi", "Kanchipuram", "Kanyakumari", "Karur", 
        "Krishnagiri", "Madurai", "Nagapattinam", "Namakkal", "Nilgiris", "Perambalur", 
        "Pudukkottai", "Ramanathapuram", "Salem", "Sivaganga", "Tenkasi", "Thanjavur", 
        "The Nilgiris", "Theni", "Tiruvallur", "Tiruchirappalli", "Tirunelveli", 
        "Tirupattur", "Vellore", "Virudhunagar"
    ],
    "West Bengal": [
        "Alipurduar", "Bankura", "Birbhum", "Cooch Behar", "Dakshin Dinajpur", "Darjeeling", 
        "Hooghly", "Howrah", "Jalpaiguri", "Jhargram", "Kalimpong", "Kolkata", "Malda", 
        "Murshidabad", "Nadia", "North 24 Parganas", "Paschim Bardhaman", "Paschim Medinipur", 
        "Purba Bardhaman", "Purba Medinipur", "Purulia", "South 24 Parganas", "Uttar Dinajpur"
    ],
    "Kerala": [
        "Alappuzha", "Ernakulam", "Idukki", "Kottayam", "Kozhikode", "Malappuram", 
        "Palakkad", "Pathanamthitta", "Thrissur", "Wayanad"
    ],
    "Rajasthan": [
        "Ajmer", "Alwar", "Banswara", "Baran", "Barmer", "Bhilwara", "Bikaner", "Bundi", 
        "Chittorgarh", "Churu", "Dausa", "Dholpur", "Dungarpur", "Hanumangarh", "Jaipur", 
        "Jaisalmer", "Jalore", "Jhalawar", "Jhunjhunu", "Jodhpur", "Karauli", "Kota", 
        "Nagaur", "Pali", "Pratapgarh", "Rajsamand", "Sawai Madhopur", "Sikar", "Sirohi", 
        "Tonk", "Udaipur"
    ],
    "Delhi": [
        "Central Delhi", "East Delhi", "New Delhi", "North Delhi", "North East Delhi", 
        "North West Delhi", "Shahdara", "South Delhi", "South West Delhi", "West Delhi"
    ],
    "Gujarat": [
        "Ahmedabad", "Amreli", "Anand", "Banaskantha", "Bharuch", "Bhavnagar", "Botad", 
        "Chhota Udepur", "Dahod", "Dang", "Gandhinagar", "Jamnagar", "Junagadh", "Kheda", 
        "Kutch", "Mahisagar", "Mehsana", "Narmada", "Navsari", "Panchmahal", "Patan", "Purna", 
        "Rajkot", "Sabarkantha", "Surat", "Surendranagar", "Tapi", "Vadodara", "Valsad"
    ],
    "Chhattisgarh": [
        "Balod", "Baloda Bazar", "Balrampur", "Bemetara", "Bijapur", "Bilaspur", "Dantewada", 
        "Dhamtari", "Durg", "Gariaband", "Janjgir-Champa", "Jashpur", "Korba", "Koriya", 
        "Raigarh", "Raipur", "Rajnandgaon", "Sukma", "Surguja"
    ],
    "Madhya Pradesh": [
        "Alirajpur", "Anuppur", "Ashok Nagar", "Balaghat", "Barwani", "Betul", "Bhind", 
        "Bhopal", "Burhanpur", "Chhindwara", "Damoh", "Datia", "Dewas", "Dhar", "Dindori", 
        "Guna", "Gwalior", "Harda", "Hoshangabad", "Indore", "Jabalpur", "Jhabua", "Katni", 
        "Khandwa", "Khargone", "Mandla", "Mandsaur", "Morena", "Narsinghpur", "Neemuch", 
        "Pachmarhi", "Panna", "Raisen", "Rajgarh", "Ratlam", "Rewa", "Sagar", "Satna", 
        "Sehore", "Seoni", "Shahdol", "Shajapur", "Sheopur", "Shivpuri", "Sidhi", "Singrauli", 
        "Tikamgarh", "Ujjain", "Umaria", "Vidisha"
    ]
}

# -------------- DATABASE SETUP --------------
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password_hash TEXT
        )
    ''')
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_user(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT password_hash FROM users WHERE username = ?', (username,))
    result = cursor.fetchone()
    conn.close()
    return result and result[0] == hash_password(password)

# -------------- WEATHER FUNCTIONS --------------
def get_weather_data(location):
    url = f"http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={location}&days=5&aqi=no"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None

def get_temperature(location, units):
    data = get_weather_data(location)
    if not data:
        return [], [], []

    days, temp_min, temp_max = [], [], []
    for day in data['forecast']['forecastday']:
        days.append(day['date'])
        temp_min.append(day['day']['mintemp_c'] if units == 'celsius' else day['day']['mintemp_f'])
        temp_max.append(day['day']['maxtemp_c'] if units == 'celsius' else day['day']['maxtemp_f'])

    return days, temp_min, temp_max

def init_plot():
    plt.style.use('ggplot')
    fig, ax = plt.subplots()
    ax.set_xlabel('Day')
    ax.set_ylabel(f'Temperature ({sign}C)')
    ax.set_title("5-Day Weather Forecast")
    return fig, ax

def plot_temperature(location, units):
    fig, ax = init_plot()
    days, temp_min, temp_max = get_temperature(location, units)
    days = dates.date2num([datetime.strptime(d, "%Y-%m-%d") for d in days])

    ax.bar(days - 0.25, temp_min, width=0.5, color='#42bff4', label='Min')
    ax.bar(days + 0.25, temp_max, width=0.5, color='#ff5349', label='Max')

    ax.set_xticks(days)
    ax.xaxis.set_major_formatter(dates.DateFormatter('%b %d'))
    ax.legend(fontsize='small')
    return fig

def plot_line_graph_temp(location, units):
    st.markdown("<h3 style='color:#ff4b4b'>📈 5-Day Temperature Trends</h3>", unsafe_allow_html=True)
    fig, ax = init_plot()
    days, temp_min, temp_max = get_temperature(location, units)
    days = dates.date2num([datetime.strptime(d, "%Y-%m-%d") for d in days])

    ax.plot(days, temp_min, label='Min Temp', color='#42bff4', marker='o')
    ax.plot(days, temp_max, label='Max Temp', color='#ff5349', marker='o')

    ax.set_xticks(days)
    ax.xaxis.set_major_formatter(dates.DateFormatter('%b %d'))
    ax.legend(fontsize='small')
    st.pyplot(fig)

def weather_forecast(location, units):
    data = get_weather_data(location)
    if not data:
        st.error("Failed to fetch weather data.")
        return

    current = data['current']
    temp = current['temp_c'] if units == 'celsius' else current['temp_f']
    feels_like = current['feelslike_c'] if units == 'celsius' else current['feelslike_f']
    icon = f"http:{current['condition']['icon']}"

    st.image(icon, caption=current['condition']['text'].title(), width=100)
    st.markdown(f"### 🌡️ Temperature: <span style='color:#ff4b4b'><b>{round(temp)}{sign}C</b></span>", unsafe_allow_html=True)
    st.markdown(f"**🤒 Feels Like**: {round(feels_like)}{sign}C")
    st.markdown(f"**☁️ Cloud Coverage**: {current['cloud']}%")
    st.markdown(f"**💨 Wind**: {current['wind_kph']} km/h")
    st.markdown(f"**💧 Humidity**: {current['humidity']}%")
    st.markdown(f"**🧭 Pressure**: {current['pressure_mb']} mBar")
    st.markdown(f"**👁️ Visibility**: {current['vis_km']} km")

# -------------- UI + AUTH FLOW --------------
init_db()

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    if 'page' not in st.session_state:
        st.session_state.page = "Login"

    st.markdown("""
        <div style='text-align:center'>
            <img src='https://cdn-icons-png.flaticon.com/512/1164/1164954.png' width='100'/>
            <h1 style='color:#4CAF50'>Welcome to Weather Forecaster 🌤️</h1>
        </div>
    """, unsafe_allow_html=True)

    page = st.sidebar.radio("Choose Page", ["Login", "Register"], index=0 if st.session_state.page == "Login" else 1)

    if page == "Login":
        st.session_state.page = "Login"
        st.subheader("🔐 Login to your account")
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type='password', key="login_pass")

        if st.button("Login"):
            if verify_user(username, password):
                st.session_state.logged_in = True
                st.session_state.user = username
                st.success(f"✅ Welcome back, {username}!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Incorrect username or password.")

    elif page == "Register":
        st.session_state.page = "Register"
        st.subheader("🆕 Create a new account")
        new_username = st.text_input("Choose a Username", key="register_user")
        new_password = st.text_input("Choose a Password", type='password', key="register_pass")

        if st.button("Register"):
            if new_username and new_password:
                try:
                    conn = sqlite3.connect('users.db')
                    cursor = conn.cursor()
                    cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', 
                                 (new_username, hash_password(new_password)))
                    conn.commit()
                    conn.close()
                    st.success("🎉 Registration successful. Please log in.")
                    st.session_state.page = "Login"
                    time.sleep(1)
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.warning("⚠️ Username already exists. Try a new one.")
            else:
                st.warning("Please fill in all fields.")

# -------------- MAIN WEATHER PAGE --------------
else:
    st.markdown(f"""
        <div style='text-align:center;'>
            <h2 style='color:#2196f3;'>☀️ Hello, {st.session_state.user}! Here's your Weather Forecast</h2>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])
    with col1:
        state = st.selectbox("📍 Select Your State:", list(states_districts.keys()))
        location = st.selectbox("📍 Select Your District:", states_districts[state], help="Select a district from the selected state")
    with col2:
        units = st.radio("🌡️ Temperature Unit:", ('celsius', 'fahrenheit'))

    graph_type = st.selectbox("📊 Graph Type:", ('Bar Graph', 'Line Graph'))

    if st.button("📥 Show Forecast"):
        weather_forecast(location, units)
        if graph_type == 'Bar Graph':
            fig = plot_temperature(location, units)
            st.pyplot(fig)
        else:
            plot_line_graph_temp(location, units)

    st.markdown("<hr>", unsafe_allow_html=True)
    if st.button("🔓 Logout"):
        st.session_state.logged_in = False
        st.session_state.page = "Login"
        time.sleep(0.5)
        st.rerun()
