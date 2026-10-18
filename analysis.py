import pandas as pd

# Load the hotel booking dataset
df = pd.read_csv("Hotel_Bookings.csv")

# Display basic information
print("Dataset loaded successfully!")
print("\nFirst 5 rows:")
print(df.head())

print("\nDataset shape:")
print(df.shape)

print("\nColumn names:")
print(df.columns.tolist())

print("\nMissing values:")
print(df.isnull().sum()) 
# Cancellation Analysis

print("\n========== CANCELLATION ANALYSIS ==========")

# Count cancelled and non-cancelled bookings
print("\nBooking Cancellation Counts:")
print(df["is_canceled"].value_counts())

# Calculate cancellation percentage
cancellation_rate = df["is_canceled"].mean() * 100
print(f"\nCancellation Rate: {cancellation_rate:.2f}%")

# Cancellation rate by hotel type
print("\nCancellation Rate by Hotel Type:")
print(df.groupby("hotel")["is_canceled"].mean().mul(100).round(2))

# Cancellation rate by customer type
print("\nCancellation Rate by Customer Type:")
print(df.groupby("customer_type")["is_canceled"].mean().mul(100).round(2))

# Cancellation rate by deposit type
print("\nCancellation Rate by Deposit Type:")
print(df.groupby("deposit_type")["is_canceled"].mean().mul(100).round(2))

# Cancellation rate by lead time
print("\nCancellation Rate by Lead Time:")
df["lead_time_group"] = pd.cut(
    df["lead_time"],
    bins=[-1, 7, 30, 90, 180, float("inf")],
    labels=["0-7 days", "8-30 days", "31-90 days",
            "91-180 days", "181+ days"]
)
print(df.groupby("lead_time_group", observed=False)["is_canceled"].mean().mul(100).round(2))

import matplotlib.pyplot as plt

# Booking Cancellation Chart
cancellation_counts = df["is_canceled"].value_counts().sort_index()

plt.figure(figsize=(8, 5))
plt.bar(
    ["Not Cancelled", "Cancelled"],
    [
        cancellation_counts.get(0, 0),
        cancellation_counts.get(1, 0)
    ]
)

plt.title("Hotel Booking Cancellation Analysis")
plt.xlabel("Booking Status")
plt.ylabel("Number of Bookings")
plt.tight_layout()
plt.savefig("booking_cancellations.png", dpi=300)
plt.show()

print("\nChart saved as booking_cancellations.png")

# Professional Chart: Cancellation Rate by Hotel Type

import matplotlib.pyplot as plt
import pandas as pd

hotel_cancellation = (
    df.groupby("hotel")["is_canceled"]
    .mean()
    .mul(100)
    .sort_values(ascending=False)
)

plt.figure(figsize=(9, 6))

bars = plt.bar(
    hotel_cancellation.index,
    hotel_cancellation.values,
    width=0.55,
    edgecolor="black",
    linewidth=0.7
)

plt.title(
    "Booking Cancellation Rate by Hotel Type",
    fontsize=16,
    fontweight="bold",
    pad=18
)
plt.xlabel("Hotel Type", fontsize=12, fontweight="bold")
plt.ylabel("Cancellation Rate (%)", fontsize=12, fontweight="bold")
plt.ylim(0, max(hotel_cancellation.max() * 1.18, 10))
plt.grid(axis="y", linestyle="--", alpha=0.3)
plt.gca().set_axisbelow(True)

# Add percentage labels above each bar
for bar in bars:
    height = bar.get_height()
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        height,
        f"{height:.1f}%",
        ha="center",
        va="bottom",
        fontsize=12,
        fontweight="bold"
    )

plt.tight_layout()
plt.savefig(
    "cancellation_by_hotel_type.png",
    dpi=300,
    bbox_inches="tight"
)
plt.show()

print("\nCancellation rate by hotel type:")
print(hotel_cancellation.round(2).astype(str) + "%")

# Professional Chart: Monthly Booking Cancellation Trend

import matplotlib.pyplot as plt
import pandas as pd

# Convert arrival date into a proper date
df["arrival_date"] = pd.to_datetime(
    df["arrival_date_year"].astype(str) + "-" +
    df["arrival_date_month"] + "-01",
    format="%Y-%B-%d",
    errors="coerce"
)

# Calculate monthly cancellation rate
monthly_cancellation = (
    df.dropna(subset=["arrival_date"])
      .groupby("arrival_date")
      .agg(
          Total_Bookings=("is_canceled", "size"),
          Cancellation_Rate=("is_canceled", "mean")
      )
)

monthly_cancellation["Cancellation_Rate"] *= 100

fig, ax = plt.subplots(figsize=(12, 6))

ax.plot(
    monthly_cancellation.index,
    monthly_cancellation["Cancellation_Rate"],
    marker="o",
    linewidth=2.5,
    markersize=6
)

ax.set_title(
    "Monthly Hotel Booking Cancellation Rate",
    fontsize=16,
    fontweight="bold",
    pad=18
)
ax.set_xlabel("Arrival Month", fontsize=12, fontweight="bold")
ax.set_ylabel("Cancellation Rate (%)", fontsize=12, fontweight="bold")
ax.grid(True, linestyle="--", alpha=0.3)
ax.tick_params(axis="x", rotation=45)

# Label each data point
for date, row in monthly_cancellation.iterrows():
    ax.annotate(
        f'{row["Cancellation_Rate"]:.1f}%',
        (date, row["Cancellation_Rate"]),
        textcoords="offset points",
        xytext=(0, 9),
        ha="center",
        fontsize=8
    )

plt.tight_layout()
plt.savefig("monthly_cancellation_trend.png", dpi=300, bbox_inches="tight")
plt.show()

print("\nMonthly Cancellation Summary:")
print(monthly_cancellation.round(2))

# Professional Chart: Cancellation Rate by Deposit Type

import matplotlib.pyplot as plt
import pandas as pd

deposit_cancellation = (
    df.groupby("deposit_type")["is_canceled"]
    .agg(["mean", "count"])
    .rename(columns={"mean": "cancellation_rate", "count": "bookings"})
)

deposit_cancellation["cancellation_rate"] *= 100
deposit_cancellation = deposit_cancellation.sort_values(
    "cancellation_rate", ascending=False
)

fig, ax = plt.subplots(figsize=(10, 6))

bars = ax.bar(
    deposit_cancellation.index,
    deposit_cancellation["cancellation_rate"],
    width=0.6,
    edgecolor="black",
    linewidth=0.7
)

ax.set_title(
    "Booking Cancellation Rate by Deposit Type",
    fontsize=16,
    fontweight="bold",
    pad=18
)
ax.set_xlabel("Deposit Type", fontsize=12, fontweight="bold")
ax.set_ylabel("Cancellation Rate (%)", fontsize=12, fontweight="bold")
ax.set_ylim(0, max(deposit_cancellation["cancellation_rate"].max() * 1.2, 10))
ax.grid(axis="y", linestyle="--", alpha=0.3)
ax.set_axisbelow(True)

for bar, (_, row) in zip(bars, deposit_cancellation.iterrows()):
    ax.annotate(
        f'{row["cancellation_rate"]:.1f}%\n({int(row["bookings"]):,} bookings)',
        (bar.get_x() + bar.get_width() / 2, bar.get_height()),
        xytext=(0, 5),
        textcoords="offset points",
        ha="center",
        fontsize=9,
        fontweight="bold"
    )

plt.tight_layout()
plt.savefig("cancellation_by_deposit_type.png", dpi=300, bbox_inches="tight")
plt.show()

print("\nCancellation by Deposit Type:")
print(deposit_cancellation.round(2))

# Professional Chart: Cancellation Rate by Customer Type

# Professional Chart: Cancellation Rate by Customer Type

import matplotlib.pyplot as plt
import pandas as pd

customer_cancellation = (
    df.groupby("customer_type")["is_canceled"]
    .agg(["mean", "count"])
    .rename(columns={"mean": "cancellation_rate", "count": "total_bookings"})
)

customer_cancellation["cancellation_rate"] *= 100
customer_cancellation = customer_cancellation.sort_values(
    "cancellation_rate", ascending=False
)

fig, ax = plt.subplots(figsize=(10, 6))

bars = ax.bar(
    customer_cancellation.index,
    customer_cancellation["cancellation_rate"],
    width=0.6,
    edgecolor="black",
    linewidth=0.7
)

ax.set_title(
    "Booking Cancellation Rate by Customer Type",
    fontsize=16,
    fontweight="bold",
    pad=18
)
ax.set_xlabel("Customer Type", fontsize=12, fontweight="bold")
ax.set_ylabel("Cancellation Rate (%)", fontsize=12, fontweight="bold")
ax.set_ylim(0, max(customer_cancellation["cancellation_rate"].max() * 1.2, 10))
ax.grid(axis="y", linestyle="--", alpha=0.3)
ax.set_axisbelow(True)

for bar, (_, row) in zip(bars, customer_cancellation.iterrows()):
    ax.annotate(
        f'{row["cancellation_rate"]:.1f}%\n'
        f'({int(row["total_bookings"]):,} bookings)',
        (bar.get_x() + bar.get_width() / 2, bar.get_height()),
        xytext=(0, 5),
        textcoords="offset points",
        ha="center",
        fontsize=9,
        fontweight="bold"
    )

plt.tight_layout()
plt.savefig("cancellation_by_customer_type.png", dpi=300, bbox_inches="tight")
plt.show()

print("\nCancellation by Customer Type:")
print(customer_cancellation.round(2))

# Professional Chart: Cancellation Rate by Lead Time

import matplotlib.pyplot as plt
import pandas as pd

# Group bookings by lead time
lead_bins = [-1, 7, 30, 90, 180, float("inf")]
lead_labels = [
    "0–7 days",
    "8–30 days",
    "31–90 days",
    "91–180 days",
    "181+ days"
]

df["lead_time_group"] = pd.cut(
    df["lead_time"],
    bins=lead_bins,
    labels=lead_labels
)

lead_analysis = (
    df.groupby("lead_time_group", observed=False)["is_canceled"]
    .agg(["mean", "count"])
    .rename(columns={"mean": "cancellation_rate", "count": "bookings"})
)

lead_analysis["cancellation_rate"] *= 100

fig, ax = plt.subplots(figsize=(11, 6))

bars = ax.bar(
    lead_analysis.index.astype(str),
    lead_analysis["cancellation_rate"],
    edgecolor="black",
    linewidth=0.7,
    width=0.65
)

ax.set_title(
    "Booking Cancellation Rate by Lead Time",
    fontsize=16,
    fontweight="bold",
    pad=18
)
ax.set_xlabel("Days Between Booking and Arrival", fontsize=12, fontweight="bold")
ax.set_ylabel("Cancellation Rate (%)", fontsize=12, fontweight="bold")
ax.grid(axis="y", linestyle="--", alpha=0.3)
ax.set_axisbelow(True)
ax.set_ylim(0, max(lead_analysis["cancellation_rate"].max() * 1.2, 10))

for bar, (_, row) in zip(bars, lead_analysis.iterrows()):
    ax.annotate(
        f'{row["cancellation_rate"]:.1f}%\n'
        f'({int(row["bookings"]):,} bookings)',
        (bar.get_x() + bar.get_width() / 2, bar.get_height()),
        xytext=(0, 5),
        textcoords="offset points",
        ha="center",
        fontsize=9,
        fontweight="bold"
    )

plt.tight_layout()
plt.savefig("cancellation_by_lead_time.png", dpi=300, bbox_inches="tight")
plt.show()

print("\nCancellation by Lead Time:")
print(lead_analysis.round(2))

# Professional Chart: Cancellation Rate by Market Segment

import matplotlib.pyplot as plt
import pandas as pd

segment_analysis = (
    df.groupby("market_segment")["is_canceled"]
    .agg(["mean", "count"])
    .rename(columns={"mean": "cancellation_rate", "count": "bookings"})
)

segment_analysis["cancellation_rate"] *= 100
segment_analysis = segment_analysis.sort_values(
    "cancellation_rate", ascending=False
)

fig, ax = plt.subplots(figsize=(11, 6))

bars = ax.bar(
    segment_analysis.index.astype(str),
    segment_analysis["cancellation_rate"],
    edgecolor="black",
    linewidth=0.7,
    width=0.65
)

ax.set_title(
    "Booking Cancellation Rate by Market Segment",
    fontsize=16,
    fontweight="bold",
    pad=18
)
ax.set_xlabel("Market Segment", fontsize=12, fontweight="bold")
ax.set_ylabel("Cancellation Rate (%)", fontsize=12, fontweight="bold")
ax.grid(axis="y", linestyle="--", alpha=0.3)
ax.set_axisbelow(True)
ax.set_ylim(0, max(segment_analysis["cancellation_rate"].max() * 1.2, 10))
plt.xticks(rotation=25, ha="right")

for bar, (_, row) in zip(bars, segment_analysis.iterrows()):
    ax.annotate(
        f'{row["cancellation_rate"]:.1f}%\n'
        f'({int(row["bookings"]):,} bookings)',
        (bar.get_x() + bar.get_width() / 2, bar.get_height()),
        xytext=(0, 5),
        textcoords="offset points",
        ha="center",
        fontsize=9,
        fontweight="bold"
    )

plt.tight_layout()
plt.savefig("cancellation_by_market_segment.png", dpi=300, bbox_inches="tight")
plt.show()

print("\nCancellation by Market Segment:")
print(segment_analysis.round(2))

# Professional Chart: Cancellation Rate by Number of Special Requests

import matplotlib.pyplot as plt
import pandas as pd

requests_analysis = (
    df.groupby("total_of_special_requests")["is_canceled"]
    .agg(["mean", "count"])
    .rename(columns={"mean": "cancellation_rate", "count": "bookings"})
)

requests_analysis["cancellation_rate"] *= 100

fig, ax = plt.subplots(figsize=(10, 6))

bars = ax.bar(
    requests_analysis.index.astype(str),
    requests_analysis["cancellation_rate"],
    edgecolor="black",
    linewidth=0.7,
    width=0.65
)

ax.set_title(
    "Booking Cancellation Rate by Number of Special Requests",
    fontsize=15,
    fontweight="bold",
    pad=18
)
ax.set_xlabel("Number of Special Requests", fontsize=12, fontweight="bold")
ax.set_ylabel("Cancellation Rate (%)", fontsize=12, fontweight="bold")
ax.grid(axis="y", linestyle="--", alpha=0.3)
ax.set_axisbelow(True)
ax.set_ylim(0, max(requests_analysis["cancellation_rate"].max() * 1.2, 10))

for bar, (_, row) in zip(bars, requests_analysis.iterrows()):
    ax.annotate(
        f'{row["cancellation_rate"]:.1f}%\n'
        f'({int(row["bookings"]):,} bookings)',
        (bar.get_x() + bar.get_width() / 2, bar.get_height()),
        xytext=(0, 5),
        textcoords="offset points",
        ha="center",
        fontsize=9,
        fontweight="bold"
    )

plt.tight_layout()
plt.savefig(
    "cancellation_by_special_requests.png",
    dpi=300,
    bbox_inches="tight"
)
plt.show()

print("\nCancellation by Number of Special Requests:")
print(requests_analysis.round(2))
