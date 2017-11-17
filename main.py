import argparse
import json
import requests
import os
import sys


def run(token, out_dir_path, out_file_name):
    # doc: https://api.slack.com/methods/users.list
    url = 'https://slack.com/api/users.list'
    data = {
        'token': token
    }
    response = requests.post(url, data=data)

    if response.status_code != 200:
        print('Error: %s', response.json())
        sys.exit(1)

    body_json = response.json()
    if not body_json['ok']:
        print('Error: %s', response.json())
        sys.exit(2)

    members_json = body_json['members']

    full_members = []
    for member_json in members_json:
        member = Member(member_json)
        if member.is_full_member:
            full_members.append(member.export_to_json())

    print('Found full members: %s' % len(full_members))

    if not os.path.exists(out_dir_path):
        os.makedirs(out_dir_path)
    with open(os.path.join(out_dir_path, out_file_name), 'w') as outfile:
        json.dump(full_members, outfile)


class Member(object):
    def __init__(self, json):
        self.profile = MemberProfile(json['profile'])
        self.id = json['id']
        self.is_deleted = json['deleted']
        self.is_bot = json.get('is_bot', False) or self.profile.full_name == 'slackbot'
        self.is_guest = json.get('is_restricted', False) or json.get('is_ultra_restricted', False)
        self.is_full_member = not self.is_bot and not self.is_guest

    def export_to_json(self):
        return {
            'id': self.id,
            'name': self.profile.full_name,
            'image': self.profile.image,
            'image_small': self.profile.image_small,
            'image_large': self.profile.image_large,
            'email': self.profile.email,
            'is_deleted': self.is_deleted,
        }


class MemberProfile(object):
    def __init__(self, json):
        self.full_name = json['real_name']
        self.image = json.get('image_192', None)
        self.image_small = json.get('image_48', None)
        self.image_large = json.get('image_512', json.get('image_192', None))
        self.email = json.get('email', None)
        self.status_text = json.get('status_text', None)
        self.status_emoji = json.get('status_emoji', None)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--token', nargs=1, metavar='TOKEN', help="Slack token", required=True)
    parser.add_argument('-o', '--out-dir', nargs=1, metavar='PATH', help="Output directory path", required=False,
                        default='out/')
    parser.add_argument('-f', '--file-name', nargs=1, metavar='NAME', help="Output file name", required=False,
                        default='members.json')
    args = parser.parse_args()
    run(args.token, args.out_dir, args.file_name)
