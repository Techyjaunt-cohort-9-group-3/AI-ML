import pandas as pd
from pathlib import Path

# Load dataset
file_path = Path(__file__).parent / "digital_guest_experience_dataset_7000.csv"

if not file_path.exists():
    file_path = Path(__file__).parent / "data" / "digital_guest_experience_dataset_7000.csv"

df = pd.read_csv(file_path)

# Remove records where no recommendation was shown
service_data = df[
    df["recommended_service"] != "Not Shown"
]

# Find the most common recommendation for each room type and loyalty tier
recommendation_counts = (
    service_data.groupby(
        ["room_type", "loyalty_tier", "recommended_service"],
        dropna=False
    )
    .size()
    .reset_index(name="guest_records")
)

top_recommendations = (
    recommendation_counts
    .sort_values("guest_records", ascending=False)
    .drop_duplicates(["room_type", "loyalty_tier"])
)

top_recommendations["loyalty_tier"] = (
    top_recommendations["loyalty_tier"].fillna("Unknown")
)


def recommend_service(room_type, loyalty_tier):

    loyalty_tier = (
        "Unknown" if pd.isna(loyalty_tier)
        else str(loyalty_tier).strip()
    )

    matches = top_recommendations[
        (top_recommendations["room_type"].str.lower() == room_type.strip().lower()) &
        (top_recommendations["loyalty_tier"].str.lower() == loyalty_tier.lower())
    ]

    if not matches.empty:
        return matches.iloc[0]["recommended_service"]

    return service_data["recommended_service"].mode()[0]

def recommend_top_services(room_type, loyalty_tier, n=3):
        
    room_matches = service_data[

service_data["room_type"].astype(str).str.lower()
        == 
str(room_type).strip().lower()
    ]

    if pd.isna(loyalty_tier):
        matches = room_matches[
            
room_matches["loyalty_tier"].isna()
        ]
    else:
        matches = room_matches[
            
room_matches["loyalty_tier"].astype(str).str.lower()
            == 
str(loyalty_tier).strip().lower()
        ]

    # If no exact match, use the same room type
    if matches.empty:
        matches = room_matches

    # If no room-type match, use all available recommendations
    if matches.empty:
        matches = service_data

    return (
        matches["recommended_service"]
        .value_counts()
        .head(n)
        .index.tolist()
    )

def get_guest_recommendation(guest_id):

    guest = df[df["guest_id"] == guest_id]

    if guest.empty:
        return {"error": "Guest not found"}

    guest = guest.iloc[0]

    recommendations = recommend_top_services(
        guest["room_type"],
        guest["loyalty_tier"]
    )

    return {
        "guest_id": guest["guest_id"],
        "room_type": guest["room_type"],
        "loyalty_tier": guest["loyalty_tier"],
        "recommended_services": recommendations
    }