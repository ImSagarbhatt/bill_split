import pandas as pd
import boto3

users = {}
def create_user(user_id, name, email, mobile):
    users[user_id] = {
        'name': name,
        'email': email,
        'mobile': mobile,
        'balances': {}
    }

def update_balance(user_id, other_user_id, amount):
    if other_user_id in users[user_id]['balances']:
        users[user_id]['balances'][other_user_id] += amount
    else:
        users[user_id]['balances'][other_user_id] = amount

def check_balance(user_id):
    return users[user_id]['balances']

def add_expense(user_id, amount, split_bw, split_type, split_portion=None):
    if split_type == "EQUAL":
        split_equal(user_id, amount, split_bw)
    elif split_type == "EXACT":
        split_exact(user_id, amount, split_bw, split_portion)
    elif split_type == "PERCENT":
        split_percent(user_id, amount, split_bw, split_portion)
    else:
        raise Exception("Invalid split type")

def split_equal(user_id, amount, split_bw):
    share = amount / len(split_bw)
    for participant in split_bw:
        if participant != user_id:
            update_balance(participant, user_id, share)
            update_balance(user_id, participant, -share)

def split_exact(user_id, amount, split_bw, splits):
    
    if sum(splits) != amount:
        raise Exception("Total splits do not match the amount")
    
    if len(split_bw) != len(splits):
        raise Exception("Number of participants does not match number of splits")
    
    for participant, share in zip(split_bw, splits):
        if participant != user_id:
            update_balance(participant, user_id, share)
            update_balance(user_id, participant, -share)

def split_percent(user_id, amount, split_bw, percentages):
    if sum(percentages) != 100:
        raise Exception("Total percentages do not sum to 100")
    
    if len(split_bw) != len(percentages):
        raise Exception("Number of participants does not match number of percentages")
    
    for participant, percent in zip(split_bw, percentages):
        share = amount * (percent / 100)
        if participant != user_id:
            update_balance(participant, user_id, share)
            update_balance(user_id, participant, -share)


def show_balance():
    return {user_id: check_balance(user_id) for user_id in users}

def send_data_to_s3():
    data = []
    for id, info in users.items():
        for other_user_id, balance in info['balances'].items():
            data.append({
                'UserId_1': id,
                'User_1': info['name'],
                'Email_1': info['email'],
                'Mobile_1': info['mobile'],
                'UserId_2': other_user_id,
                'User_2': users[other_user_id]['name'],
                'Email_2': users[other_user_id]['email'],
                'Mobile_2': users[other_user_id]['mobile'],
                'Balance': round(balance, 2)
            })

    df = pd.DataFrame(data)
    filename = "weekly_update_file.xlsx"
    df.to_excel(filename,index=False)
    try:
        s3 = boto3.client('s3')
        bucket_name = 'your-s3-bucket-name'
        temp_file_path = filename

        s3.upload_file(filename, bucket_name, temp_file_path)
    except Exception as e:
        print("Error uploading file on S3: ",e)
        
def main():
    # create user accounts
    create_user('u1', 'sagar', 'sagar@gmail.com', '9988776655')
    create_user('u2', 'ankit', 'ankit@gmail.com', '8877665544')
    create_user('u3', 'rahul', 'rahul@gmail.com', '7766554433')
    create_user('u4', 'milan', 'milan@gmail.com', '6655443322')

    # condition one when amount is equally divided
    add_expense('u1', 1000, ['u1', 'u2', 'u3', 'u4'], 'EQUAL')
    print(show_balance())
    print("----"*30)

    # Condition two when exact amount is divided between two users
    add_expense('u1', 1250, ['u3','u4'], 'EXACT', [370, 880])
    print(show_balance())
    print("----"*30)

    # conditioin three when amount is divided between all four users and user one paid double of its percentage
    add_expense('u4', 1200, ['u1', 'u2', 'u3', 'u4'], 'PERCENT', [40, 20,20,20])
    print(show_balance())

if __name__=='__main__':
    main()


