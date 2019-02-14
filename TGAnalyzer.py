import json
import pandas as p
from Message import Message
import matplotlib.pyplot as plt


# Prints information about a message
def message_info(message):
    print("%20s | %10s | %9s | %10s |" % (message.m_author, message.m_date, message.m_time, message.m_type))


# Creates a list of Message objects from JSON file
def load_json(path):
    print("Loading JSON file...")
    # Parse JSON file
    with open(path) as file:
        data = json.load(file)
    # Convert a list of dictionaries into a list of Message objects
    m_objects = []
    for i in range(0, len(data)):
        m_objects.append(Message(data[i]["m_author"], data[i]["m_date"], data[i]["m_time"], data[i]["m_type"], None))
    print("Loading finished!")
    return m_objects


def get_list_of_authors(m_objects):
    authors = []
    for m in m_objects:
        if m.m_author not in authors:
            authors.append(m.m_author)
    return authors


# Returns two dimensional array with lists of number of messages of certain type by day with correspondence to authors
# list
# If real is true then it counts IN RANGE of dates from first to last message
def get_number_of_messages(m_objects, authors, type='all', real=False):
    counters = [0]*len(authors)
    result_list = [[] for i in range(0, len(authors))]        # Two dimensional array
    if real:
        date_first = m_objects[0].m_date
        tmp = date_first.split('.')
        date_first = tmp[1] + '.' + tmp[0] + '.' + tmp[2]
        date_last = m_objects[len(m_objects) - 1].m_date
        tmp = date_last.split('.')
        date_last = tmp[1] + '.' + tmp[0] + '.' + tmp[2]
        dates_list = p.date_range(date_first, date_last, freq='D')
        dates_list = [d.strftime("%d.%m.%Y") for d in dates_list]
        dates_list_count = 1
    else:
        dates_list = []

    # dates1 = p.date_range(date_first, date_last, freq='D')
    # dates1 = [d.strftime("%d.%m.%Y") for d in dates1]
    # dates1_count = 1
    date = m_objects[0].m_date
    for m in m_objects:
        if date != m.m_date:
            for i in range(0, len(authors)):
                result_list[i].append(counters[i])
                counters[i] = 0
            # Working with dates
            if real:
                date = dates_list[dates_list_count]
                dates_list_count += 1
            else:
                dates_list.append(date)  # Appending 'old' date
                date = m.m_date
        else:
            if type is 'all':
                for i in range(0, len(authors)):
                    if m.m_author == authors[i]:
                        counters[i] += 1
            else:
                for i in range(0, len(authors)):
                    if m.m_author == authors[i] and m.m_type == type:
                        counters[i] += 1
    # print(result_list)
    if not real:
        dates_list.append(date)
    for i in range(0, len(authors)):
        result_list[i].append(counters[i])
        counters[i] = 0

    dates_list = [d[:-4] + d[-2:] for d in dates_list]

    return result_list, dates_list


def get_total_number_of_messages(m_objects, authors, type='all'):
    messages, _ = get_number_of_messages(m_objects, authors, type)
    for i in range(0, len(messages)):
        counter = 0
        for j in range(0, len(messages[i])):
            counter += messages[i][j]
        messages[i] = counter
    return messages


# Works only for chats between two persons
def create_combined_plot(m_objects, colors=None, labels=None, real=False):
    authors = get_list_of_authors(m_objects)

    if labels is not None:
        if len(labels) != len(authors):
            print("Number of labels is not equal to number of authors!")
            labels = authors
    else:
        labels = authors

    if colors is not None:
        if len(labels) != len(authors):
            print("Number of colors is not equal to number of authors!")
            colors = None

    m_counters, dates = get_number_of_messages(m_objects, authors, real=real)
    difference = []
    for i in range(0, len(dates)):
        difference.append(m_counters[0][i]-m_counters[1][i])

    plt.figure(figsize=(len(dates) / 4, 6))

    if colors is not None:
        for i in range(0, len(authors)):
            plt.plot(dates, m_counters[i], label=labels[i], color=colors[i], marker='o', linewidth=1)
    else:
        colors = []
        for i in range(0, len(authors)):
            p = plt.plot(dates, m_counters[i], label=labels[i], marker='o', linewidth=1)
            colors.append(p[0].get_color())

    author1_bools = []
    author2_bools = []
    for i in range(0, len(difference)):
        author1_bools.append(difference[i] > 0)
        author2_bools.append(difference[i] < 0)
    if len(authors) == 2:
        plt.fill_between(dates, difference, where=author1_bools, interpolate=True, color=colors[0], alpha=0.25)
        plt.fill_between(dates, difference, where=author2_bools, interpolate=True, color=colors[1], alpha=0.25)
    plt.axhline(linestyle='-', linewidth=1, color='r')
    plt.xticks(rotation='vertical', fontsize=8)
    plt.title("Messages")
    plt.legend()
    print("Saving!")
    plt.savefig("Plot.png", dpi=200, bbox_inches='tight')