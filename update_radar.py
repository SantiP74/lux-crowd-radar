import datetime
import json
import random
import urllib.request


def fetch_live_mobility_index():
    """Calculates realistic crowd indices for Luxembourg-Ville districts

    accounting for weekday vs. weekend patterns, Sunday slowdowns, and live
    weather.
    """
    now = datetime.datetime.now()
    hour = now.hour
    weekday = now.weekday()  # 0=Monday, ..., 5=Saturday, 6=Sunday
    is_sunday = weekday == 6
    is_saturday = weekday == 5

    # 1. Hyperlocal weather correction via Open-Meteo
    rain_factor = 1.0
    try:
        meteo_url = "https://api.open-meteo.com/v1/forecast?latitude=49.6116&longitude=6.1319&current_weather=true"
        req = urllib.request.Request(
            meteo_url, headers={"User-Agent": "LuxCrowdRadar/1.0"}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            meteo_data = json.loads(response.read().decode())
            weather_code = meteo_data.get("current_weather", {}).get(
                "weathercode", 0
            )
            if weather_code >= 51:
                rain_factor = (
                    0.70  # Rain clears outdoor areas and reduces walking flows
                )
    except Exception:
        rain_factor = 1.0

    def compute_district(name, base_occupancy, variance, reason_live):
        noise = random.randint(-variance, variance)
        level = int((base_occupancy + noise) * rain_factor)
        level = max(5, min(95, level))

        trend_val = random.randint(-8, 8)
        trend_str = (
            f"+{trend_val}% last 20 min"
            if trend_val >= 0
            else f"{trend_val}% last 20 min"
        )
        return {
            "level": level,
            "trend": trend_str,
            "trend_type": "up" if trend_val >= 0 else "down",
            "reason": reason_live,
        }

    # 2. Dynamic profiles based on day and hour
    if is_sunday:
        # SUNDAY SCHEDULE: Quiet city, retail closed, minimal transit
        if hour < 12:
            # Sunday Morning (Deep calm across the city)
            v_haute = compute_district(
                "Ville-Haute",
                12,
                3,
                "Quiet Sunday morning, commercial retail closed",
            )
            gare = compute_district(
                "Gare", 18, 4, "Reduced Sunday regional transit rhythm"
            )
            grund = compute_district(
                "Grund & Clausen",
                15,
                3,
                "Tranquil valley, morning walking/running",
            )
            kirchberg = compute_district(
                "Kirchberg", 8, 2, "Office district completely idle"
            )
            limperts = compute_district(
                "Limpertsberg", 14, 3, "Calm residential morning"
            )
            belair = compute_district(
                "Belair & Merl",
                20,
                4,
                "Local morning strolls & park activities",
            )
            gasperich = compute_district(
                "Gasperich / Cloche d'Or",
                10,
                2,
                "Shopping mall closed, very low activity",
            )
            bonnevoie = compute_district(
                "Bonnevoie", 15, 3, "Quiet neighbourhood streets"
            )
        elif 12 <= hour < 18:
            # Sunday Afternoon (Mild family walks, open cafes)
            v_haute = compute_district(
                "Ville-Haute",
                38,
                5,
                "Afternoon visitors, open cafes on Place d'Armes",
            )
            gare = compute_district(
                "Gare", 30, 4, "Moderate afternoon passenger transit"
            )
            grund = compute_district(
                "Grund & Clausen", 42, 6, "Afternoon walks along the Alzette"
            )
            kirchberg = compute_district(
                "Kirchberg", 18, 4, "Cultural visitors (Mudam / Philharmonie)"
            )
            limperts = compute_district(
                "Limpertsberg", 22, 3, "Relaxed residential afternoon"
            )
            belair = compute_district(
                "Belair & Merl", 35, 5, "Parc de Merl family recreational flow"
            )
            gasperich = compute_district(
                "Gasperich / Cloche d'Or",
                15,
                3,
                "Low commercial activity on Sunday",
            )
            bonnevoie = compute_district(
                "Bonnevoie", 25, 4, "Local leisure and neighbourhood cafes"
            )
        else:
            # Sunday Evening
            v_haute = compute_district(
                "Ville-Haute", 28, 4, "Evening dining, low street footfall"
            )
            gare = compute_district(
                "Gare", 35, 5, "End-of-weekend inbound rail returns"
            )
            grund = compute_district(
                "Grund & Clausen", 32, 5, "Moderate evening tavern activity"
            )
            kirchberg = compute_district(
                "Kirchberg", 10, 2, "Quiet business district"
            )
            limperts = compute_district(
                "Limpertsberg", 12, 2, "Calm residential evening"
            )
            belair = compute_district(
                "Belair & Merl", 10, 2, "Quiet residential evening"
            )
            gasperich = compute_district(
                "Gasperich / Cloche d'Or", 12, 2, "Quiet commercial perimeter"
            )
            bonnevoie = compute_district(
                "Bonnevoie", 20, 3, "Low evening traffic"
            )

    elif is_saturday:
        # SATURDAY SCHEDULE: Busy retail, lively night
        if 13 <= hour <= 19:
            v_haute = compute_district(
                "Ville-Haute",
                86,
                5,
                "Peak Saturday retail footfall & Grand-Rue shopping",
            )
            gare = compute_district(
                "Gare", 72, 5, "Commercial traffic & weekend tram connections"
            )
            grund = compute_district(
                "Grund & Clausen", 55, 6, "Afternoon leisure and river walks"
            )
            kirchberg = compute_district(
                "Kirchberg", 35, 4, "Cinema (Kinepolis) & shopping visitors"
            )
            limperts = compute_district(
                "Limpertsberg", 30, 4, "Glacis weekend visitors"
            )
            belair = compute_district(
                "Belair & Merl", 35, 4, "Parks and residential calm"
            )
            gasperich = compute_district(
                "Gasperich / Cloche d'Or",
                82,
                5,
                "Cloche d'Or shopping mall high Saturday rush",
            )
            bonnevoie = compute_district(
                "Bonnevoie", 45, 4, "Neighbourhood bars and cafes"
            )
        elif hour >= 20:
            v_haute = compute_district(
                "Ville-Haute", 84, 5, "Saturday dinner & bar nightlife"
            )
            gare = compute_district(
                "Gare", 65, 5, "Night transport and transit"
            )
            grund = compute_district(
                "Grund & Clausen",
                88,
                4,
                "Peak weekend nightlife along Rives de Clausen",
            )
            kirchberg = compute_district(
                "Kirchberg", 25, 4, "Evening dining and events"
            )
            limperts = compute_district(
                "Limpertsberg", 25, 3, "Quiet residential"
            )
            belair = compute_district("Belair & Merl", 15, 2, "Quiet evening")
            gasperich = compute_district(
                "Gasperich / Cloche d'Or", 30, 4, "Post-retail outflow"
            )
            bonnevoie = compute_district(
                "Bonnevoie", 58, 5, "Active local restaurants and pubs"
            )
        else:
            v_haute = compute_district(
                "Ville-Haute", 45, 5, "Morning shoppers arriving"
            )
            gare = compute_district(
                "Gare", 48, 4, "Weekend morning transit hub"
            )
            grund = compute_district(
                "Grund & Clausen", 20, 3, "Morning quiet"
            )
            kirchberg = compute_district(
                "Kirchberg", 18, 3, "Low morning activity"
            )
            limperts = compute_district(
                "Limpertsberg", 22, 3, "Local bakeries & market"
            )
            belair = compute_district(
                "Belair & Merl", 25, 3, "Morning outdoor activity"
            )
            gasperich = compute_district(
                "Gasperich / Cloche d'Or", 40, 5, "Retail opening hour"
            )
            bonnevoie = compute_district(
                "Bonnevoie", 30, 3, "Morning neighbourhood movement"
            )

    else:
        # WEEKDAY SCHEDULE (Monday to Friday: commuting, lunch rush, evening dining)
        if 7 <= hour <= 9 or 16 <= hour <= 19:
            # Rush Hour
            v_haute = compute_district(
                "Ville-Haute", 75, 5, "Commuter tram transit & retail activity"
            )
            gare = compute_district(
                "Gare", 85, 4, "High commuter train/tram interchange"
            )
            grund = compute_district(
                "Grund & Clausen", 30, 4, "Normal local flow"
            )
            kirchberg = compute_district(
                "Kirchberg", 88, 4, "Peak business & institutional commuter rush"
            )
            limperts = compute_district(
                "Limpertsberg", 45, 4, "School and university rush hour"
            )
            belair = compute_district(
                "Belair & Merl", 35, 4, "School drop-off & exit traffic"
            )
            gasperich = compute_district(
                "Gasperich / Cloche d'Or",
                78,
                5,
                "Commuter traffic & business park inflow",
            )
            bonnevoie = compute_district(
                "Bonnevoie", 60, 4, "Commuter artery to Gare central"
            )
        elif 12 <= hour <= 14:
            # Lunch Rush
            v_haute = compute_district(
                "Ville-Haute",
                80,
                4,
                "Lunchtime dining rush & pedestrian footfall",
            )
            gare = compute_district(
                "Gare", 65, 4, "Mid-day commercial movement"
            )
            grund = compute_district(
                "Grund & Clausen", 38, 4, "Lunch crowd in lower town"
            )
            kirchberg = compute_district(
                "Kirchberg", 75, 4, "Lunch hour around Infinity & European area"
            )
            limperts = compute_district(
                "Limpertsberg", 40, 3, "Student & residential lunch"
            )
            belair = compute_district(
                "Belair & Merl", 25, 3, "Local neighbourhood lunch"
            )
            gasperich = compute_district(
                "Gasperich / Cloche d'Or",
                68,
                4,
                "Cloche d'Or dining terrace rush",
            )
            bonnevoie = compute_district(
                "Bonnevoie", 40, 3, "Neighbourhood bistros"
            )
        elif 19 <= hour <= 23:
            # Weekday Evening
            v_haute = compute_district(
                "Ville-Haute", 65, 5, "Evening dining footfall"
            )
            gare = compute_district(
                "Gare", 55, 4, "Evening passenger connections"
            )
            grund = compute_district(
                "Grund & Clausen", 68, 5, "River pubs and dinner gatherings"
            )
            kirchberg = compute_district(
                "Kirchberg", 20, 3, "Post-work empty offices"
            )
            limperts = compute_district(
                "Limpertsberg", 18, 2, "Quiet residential evening"
            )
            belair = compute_district(
                "Belair & Merl", 15, 2, "Quiet residential"
            )
            gasperich = compute_district(
                "Gasperich / Cloche d'Or", 35, 4, "Cinema & late dining"
            )
            bonnevoie = compute_district(
                "Bonnevoie", 45, 4, "Local dining and pub flow"
            )
        else:
            # Regular off-peak hours
            v_haute = compute_district(
                "Ville-Haute", 45, 4, "Moderate pedestrian traffic"
            )
            gare = compute_district("Gare", 50, 4, "Steady transit hub" if hour >= 6 else 15)
            grund = compute_district("Grund & Clausen", 18, 3, "Calm lower town")
            kirchberg = compute_district("Kirchberg", 42, 4, "Standard business activity")
            limperts = compute_district("Limpertsberg", 22, 3, "Calm residential")
            belair = compute_district("Belair & Merl", 18, 2, "Quiet parks")
            gasperich = compute_district("Gasperich / Cloche d'Or", 45, 4, "Retail and offices")
            bonnevoie = compute_district("Bonnevoie", 30, 3, "Local neighbourhood flow")

    geojson_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "name": "Ville-Haute (Historic City Centre)",
                    "crowd_level": v_haute["level"],
                    "trend": v_haute["trend"],
                    "trend_type": v_haute["trend_type"],
                    "reason": v_haute["reason"],
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[6.1240, 49.6135], [6.1335, 49.6145], [6.1345, 49.6090], [6.1265, 49.6085], [6.1240, 49.6135]]],
                },
            },
            {
                "type": "Feature",
                "properties": {
                    "name": "Gare",
                    "crowd_level": gare["level"],
                    "trend": gare["trend"],
                    "trend_type": gare["trend_type"],
                    "reason": gare["reason"],
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[6.1250, 49.6040], [6.1370, 49.6040], [6.1360, 49.5960], [6.1270, 49.5965], [6.1250, 49.6040]]],
                },
            },
            {
                "type": "Feature",
                "properties": {
                    "name": "Kirchberg",
                    "crowd_level": kirchberg["level"],
                    "trend": kirchberg["trend"],
                    "trend_type": kirchberg["trend_type"],
                    "reason": kirchberg["reason"],
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[6.1370, 49.6200], [6.1750, 49.6380], [6.1850, 49.6280], [6.1450, 49.6150], [6.1370, 49.6200]]],
                },
            },
            {
                "type": "Feature",
                "properties": {
                    "name": "Limpertsberg",
                    "crowd_level": limperts["level"],
                    "trend": limperts["trend"],
                    "trend_type": limperts["trend_type"],
                    "reason": limperts["reason"],
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[6.1150, 49.6180], [6.1300, 49.6270], [6.1360, 49.6170], [6.1230, 49.6140], [6.1150, 49.6180]]],
                },
            },
            {
                "type": "Feature",
                "properties": {
                    "name": "Grund & Clausen",
                    "crowd_level": grund["level"],
                    "trend": grund["trend"],
                    "trend_type": grund["trend_type"],
                    "reason": grund["reason"],
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[6.1335, 49.6090], [6.1420, 49.6150], [6.1460, 49.6110], [6.1360, 49.6060], [6.1335, 49.6090]]],
                },
            },
            {
                "type": "Feature",
                "properties": {
                    "name": "Belair & Merl",
                    "crowd_level": belair["level"],
                    "trend": belair["trend"],
                    "trend_type": belair["trend_type"],
                    "reason": belair["reason"],
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[6.1030, 49.6130], [6.1220, 49.6120], [6.1210, 49.6010], [6.1010, 49.6030], [6.1030, 49.6130]]],
                },
            },
            {
                "type": "Feature",
                "properties": {
                    "name": "Gasperich / Cloche d'Or",
                    "crowd_level": gasperich["level"],
                    "trend": gasperich["trend"],
                    "trend_type": gasperich["trend_type"],
                    "reason": gasperich["reason"],
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[6.1100, 49.5930], [6.1300, 49.5930], [6.1270, 49.5780], [6.1080, 49.5790], [6.1100, 49.5930]]],
                },
            },
            {
                "type": "Feature",
                "properties": {
                    "name": "Bonnevoie",
                    "crowd_level": bonnevoie["level"],
                    "trend": bonnevoie["trend"],
                    "trend_type": bonnevoie["trend_type"],
                    "reason": bonnevoie["reason"],
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[6.1360, 49.6040], [6.1550, 49.6020], [6.1480, 49.5880], [6.1350, 49.5930], [6.1360, 49.6040]]],
                },
            },
        ],
    }

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(geojson_data, f, indent=2, ensure_ascii=False)
    print("✅ data.json successfully updated with Sunday/Weekday logic!")


if __name__ == "__main__":
    fetch_live_mobility_index()
