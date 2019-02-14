import os
import re
from bs4 import BeautifulSoup as __BeautifulSoup
from Message import Message as __Message


# Sort list of names in a natural order (0, 1, ..., 9, 10) instead of (0, 10, 11, 12)
def __sorted_alphanumeric(data):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(data, key=alphanum_key)


# Can return 'None' if it is not a message from a person, or an object of 'Message'class
# So this moment needs to be checked
def __parse_message(bf4_item, prev_author=None):
    result = bf4_item.get('class')

    # Check if it is a real message
    if 'service' in result:
        return None

    # Getting author of a message
    m_author = bf4_item.find('div', {'class': 'from_name'})
    if m_author is None or 'joined' in result:
        m_author = prev_author
    else:
        m_author = m_author.get_text().replace('\n', '').replace(' ', '')

    # Getting date and time of a message
    m_date = bf4_item.find('div', {'class': 'date'})
    result = m_date.get('title').split(sep=' ')
    m_date = result[0]
    m_time = result[1]

    # Getting message type (text, sticker, etc)
    m_type = 'other'
    if bf4_item.find('div', {'class': 'text'}) is not None:
        m_type = 'text'
    elif bf4_item.find('img', {'class': 'sticker'}) is not None:
        m_type = 'sticker'
    elif bf4_item.find('div', {'class': 'title bold'}) is not None:
        if bf4_item.find('div', {'class': 'title bold'}).get_text().replace('\n', '').replace(' ', '') == "Sticker":
            m_type = 'sticker'

    return __Message(m_author, m_date, m_time, m_type, None)


# Gets path to messages.html from tg chat history and returns list of message objects
def get_list_of_messages(path):
    soup = __BeautifulSoup(open(path, encoding='utf-8'), 'html.parser')
    messages = soup.find_all('div', {'class': 'message'})
    m_objects = []
    cur_author = None
    num_of_messages = len(messages)
    for i in range(0, num_of_messages):
        print("\r%15s completed %6.2f%%" % (path, ((i/num_of_messages)*100)), end='')
        m = __parse_message(messages[i], cur_author)
        if m is not None:
            cur_author = m.m_author
            m_objects.append(m)
    print("\r%15s completed %6.2f%%" % (path, 100))
    return m_objects


# Create JSON file from telegram html history files
def convert_to_json(path, name=None):
    if name is None:
        name = 'messages.json'

    # Prepare history files
    if os.path.isfile(os.path.join(path, "messages.html")):
        os.rename(os.path.join(path, "messages.html"), os.path.join(path, "messages1.html"))
    chat_html_files = __sorted_alphanumeric(os.listdir(path))

    # Parse all history files
    m_objects = []
    for i in range(0, len(chat_html_files)):
        m_objects += get_list_of_messages(os.path.join(path, chat_html_files[i]))

    # Create JSON file and save all messages in it
    json_file = open(name, 'w')
    json_file.write("[\n")
    for i in range(0, len(m_objects)-1):
        json_file.write(m_objects[i].to_json() + ",\n")
    json_file.write(m_objects[len(m_objects)-1].to_json() + "\n")
    json_file.write("]")
    print("Conversion to JSON is finished!")
