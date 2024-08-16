import numpy as np
import pandas as pd
import math

def leave_one_out_split(outfit_ids, groups, derived_booking_times):
    outfit_ids, groups, derived_booking_times = np.array(outfit_ids), np.array(groups), np.array(derived_booking_times)
    sorted_indices = np.argsort(derived_booking_times)
    return outfit_ids[sorted_indices[:-1]], outfit_ids[sorted_indices[-1]], groups[sorted_indices[:-1]], groups[sorted_indices[-1]], derived_booking_times[sorted_indices[:-1]], derived_booking_times[sorted_indices[-1]]

def leave_one_out_split_unique(outfit_ids, groups, derived_booking_times):
    outfit_ids, groups, derived_booking_times = np.array(outfit_ids), np.array(groups), np.array(derived_booking_times)
    
    sorted_indices = np.argsort(derived_booking_times)
    sorted_outfit_ids = outfit_ids[sorted_indices]
    sorted_groups = groups[sorted_indices]
    sorted_booking_times = derived_booking_times[sorted_indices]
    
    unique_groups, counts = np.unique(sorted_groups, return_counts=True)
    
    single_count_indices = np.where(counts == 1)[0]
    if len(single_count_indices) == 0:
        print(f"No unique outfit found with groups {groups}")
        return None
    
    unique_group = unique_groups[single_count_indices[0]]
    unique_group_index = np.where(sorted_groups == unique_group)[0][0]
    remaining_indices = np.arange(len(sorted_groups)) != unique_group_index
    
    return (
        sorted_outfit_ids[remaining_indices], sorted_outfit_ids[unique_group_index],
        sorted_groups[remaining_indices], sorted_groups[unique_group_index],
        sorted_booking_times[remaining_indices], sorted_booking_times[unique_group_index]
    )

def leave_percentage_out_split(outfit_ids, groups, derived_booking_times, percentage=0.2):
    outfit_ids, groups, derived_booking_times = np.array(outfit_ids), np.array(groups), np.array(derived_booking_times)
    num_to_leave = max(math.floor(len(outfit_ids) * percentage), 1)

    sorted_indices = np.argsort(derived_booking_times)
    return outfit_ids[sorted_indices[:-num_to_leave]], outfit_ids[sorted_indices[-num_to_leave:]], groups[sorted_indices[:-num_to_leave]], groups[sorted_indices[-num_to_leave:]], derived_booking_times[sorted_indices[:-num_to_leave]], derived_booking_times[sorted_indices[-num_to_leave:]]

# def leave_percentage_out_split_unique(outfit_ids, groups, derived_booking_times, percentage=0.2):
#     outfit_ids, groups, derived_booking_times = np.array(outfit_ids), np.array(groups), np.array(derived_booking_times)
#     num_to_leave = max(math.floor(len(outfit_ids) * percentage), 1)

#     sorted_indices = np.argsort(derived_booking_times)
#     sorted_outfit_ids = outfit_ids[sorted_indices]
#     sorted_groups = groups[sorted_indices]
#     sorted_booking_times = derived_booking_times[sorted_indices]
    
#     unique_groups, counts = np.unique(sorted_groups, return_counts=True)
    
#     single_count_indices = np.where(counts == 1)[0]
#     if len(single_count_indices) == 0:
#         print(f"No unique outfit found with groups {groups}")
#         return None
    
#     single_count_subset = single_count_indices if len(single_count_indices) < num_to_leave else single_count_indices[:num_to_leave]
#     unique_groups = unique_groups[single_count_subset]
#     remaining_indices = [i for i in np.arange(len(sorted_groups)) if i not in single_count_subset]

#     return (
#         sorted_outfit_ids[remaining_indices], sorted_outfit_ids[single_count_subset],
#         sorted_groups[remaining_indices], sorted_groups[single_count_subset],
#         sorted_booking_times[remaining_indices], sorted_booking_times[single_count_subset]
#     )

def leave_percentage_out_split_unique(outfit_ids, groups, derived_booking_times, percentage=0.2):
    outfit_ids, groups, derived_booking_times = np.array(outfit_ids), np.array(groups), np.array(derived_booking_times)
    num_to_leave = max(math.floor(len(outfit_ids) * percentage), 1)

    sorted_indices = np.argsort(derived_booking_times)
    sorted_outfit_ids = outfit_ids[sorted_indices]
    sorted_groups = groups[sorted_indices]
    sorted_booking_times = derived_booking_times[sorted_indices]
    
    unique_groups, counts = np.unique(sorted_groups, return_counts=True)
    
    single_count_indices = np.where(counts == 1)[0]
    if len(single_count_indices) == 0:
        print(f"No unique outfit found with groups {groups}")
        return None
    
    # Find the actual indices in the sorted arrays where the unique groups are located
    unique_group_mask = np.isin(sorted_groups, unique_groups[single_count_indices])
    
    # Indices of single count elements
    single_count_actual_indices = np.where(unique_group_mask)[0]
    
    # Limit to the number to leave out based on the percentage
    if len(single_count_actual_indices) > num_to_leave:
        single_count_actual_indices = single_count_actual_indices[:num_to_leave]

    # Remaining indices that are not in single_count_actual_indices
    remaining_indices = np.setdiff1d(np.arange(len(sorted_groups)), single_count_actual_indices)
    
    return (
        sorted_outfit_ids[remaining_indices], sorted_outfit_ids[single_count_actual_indices],
        sorted_groups[remaining_indices], sorted_groups[single_count_actual_indices],
        sorted_booking_times[remaining_indices], sorted_booking_times[single_count_actual_indices]
    )

def convert_user_orders_to_train_test_splits(user_orders_df, date_column="rentalPeriod.start", percentage_test=None):
    
    if percentage_test is not None:
        user_splits = user_orders_df.apply(lambda x: leave_percentage_out_split(x["outfit.id"], x["group"], x[date_column], percentage=percentage_test), axis=1)
    else:
        user_splits = user_orders_df.apply(lambda x: leave_one_out_split(x["outfit.id"], x["group"], x[date_column]), axis=1)
    
    user_splits_df = pd.DataFrame(user_splits.tolist(), columns=["train_outfit_ids", "test_outfit_id", "train_group", "test_group", "train_booking_times", "test_booking_time"])
    if percentage_test is not None:
        user_splits_unique = user_orders_df.apply(lambda x: leave_percentage_out_split_unique(x["outfit.id"], x["group"], x[date_column], percentage=percentage_test), axis=1)
    else:
        user_splits_unique = user_orders_df.apply(lambda x: leave_one_out_split_unique(x["outfit.id"], x["group"], x[date_column]), axis=1)
    user_splits_unique_df = pd.DataFrame(user_splits_unique.tolist(), columns=["train_outfit_ids", "test_outfit_id", "train_group", "test_group", "train_booking_times", "test_booking_time"])
    user_splits_unique_df = user_splits_unique_df.dropna()
    return user_splits_df, user_splits_unique_df

# Some entries among the triplet data have been rented twice for within short time intervals. Often, these are mistaken entries and should be removed.
# Other times the outfit has been rented for two consecutive months, regardless we should remove these entries.
def remove_consecutive_duplicates(user_triplets_df, date_column="rentalPeriod.start"):
    user_triplets_df[date_column] = pd.to_datetime(user_triplets_df[date_column])

    drop_indexes = []
    for i, (customer_id, group) in enumerate(user_triplets_df.groupby('customer.id')):
        # Check if any repeated outfit ids have less than a month between booking times.
        repeated_ids = group["outfit.id"].value_counts() > 1
        for repeated_id in repeated_ids[repeated_ids].index:
            repeated_subset = group[group["outfit.id"] == repeated_id]
            previous_entry_index = 0 # Since we'll occasionally find more than two repeated entries, we need to keep track of the last valid index we have.
            for i in range(1, repeated_subset.shape[0]):
                if (repeated_subset.iloc[i][date_column] - repeated_subset.iloc[previous_entry_index][date_column]).days < 30:
                    drop_indexes.append(repeated_subset.index[i])
                else:
                    previous_entry_index = i

    print(len(drop_indexes))
    user_triplets_df = user_triplets_df.drop(drop_indexes)    
    return user_triplets_df

# Convert the triplets format with one transaction per row to a format all transactions per user
def translate_user_triplets_to_orders(user_triplets_df, outfits_df):    
    # Translate the outfit ids to outfit groups before aggregating
    id_group_dict = outfits_df[["id", "group"]].to_dict(orient="records")
    id_group_dict = {x["id"]: x["group"] for x in id_group_dict}
    user_triplets_df["group"] = user_triplets_df["outfit.id"].map(id_group_dict)

    # Aggregate the outfit ids, groups, validFrom and bookingTime for each user
    user_orders_df = user_triplets_df.groupby("customer.id").agg({"outfit.id": list, "group":list, "rentalPeriod.start":list, "rentalPeriod.end":list}).reset_index()
    user_orders_df["num_orders"] = user_orders_df["outfit.id"].apply(lambda x: len(x))
    user_orders_df = user_orders_df[user_orders_df["num_orders"] > 1]
    return user_orders_df