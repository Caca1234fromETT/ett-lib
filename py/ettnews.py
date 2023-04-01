ETTNEWS_KEY = "pcu272/enn/"
# ETTNEWS_KEY should be correct otherwise you'll have an error

import json
import ett
import datetime

# returns dictionary of JSON data
# name: name of the root page containing the JSON data
def get_enn(name):
    content = ett.get(name)
    return json.loads(content)

# posts stringified dictionary of JSON data
# name: name of the root page to contain the JSON data
def post_enn(name, data):
    content = json.dumps(data)
    ett.post(name, content)

# returns the name of the page containing the JSON data
# name: name of the root page that should display the JSON data
def get_enn_url(name):
    return ETTNEWS_KEY + name

# returns data string from JSON data
# data: dictionary of JSON data
# key: name of string
# placeholder: value returned if "key" is invalid
# Used when data is already get
def get_data_string_local(data, key, placeholder):
    if key in data["strings"]:
        return data["strings"][key]
    return placeholder

# [unused?] sets local data string
def set_data_string_local(data, key, value):
    data["strings"][key] = value

# posts stringified JSON data containing modified data strings
# name: name of the root page to display
# key: name of the string
# value: value of the string
def set_data_string(name, key, value):
    data = get_enn(get_enn_url(name))
    set_data_string_local(data, key, value)
    post_enn(get_enn_url(name), data)

# returns the index of the last character preceding a paragraph end or the end of file
def get_article_start_end(content):
    index = content.find("\n\n")
    if index == -1:
        return len(content)
    return index

# returns the article start section (with message if incomplete)
def get_article_start(content):
    index = get_article_start_end(content)
    if index == len(content):
        return content
    return content[:index] + "\n\n(continue reading at article page)"

# [unused?]
def get_article_with_ad(content, ad, index):
    return content[:index] + "\n\n═══════════════════════════════════════════════\n[AD] " + ad + "\n═══════════════════════════════════════════════" + content[index:]

def list_articles(name, num = 20, root_title_length = 50, show_featured = False, authored_titles = False):
    # Get JSON data
    data = get_enn(get_enn_url(name))
    length = len(data["art"])
    header = get_data_string_local(data, "rootHeader", "/" + name)
    article_header = get_data_string_local(data, "articleHeader", "Article")
    ads = get_data_string_local(data, "ads", ["Error: No ads."])
    ad = ads[int(datetime.datetime.now().strftime("%d")) % len(ads)]

    # Get start index
    start_index = max(0, length - num)

    # Process articles
    featured = ""
    article_list = ""
    for x in range(start_index, length):
        item = data["art"][x]
        content_data = item["content"]
        article_url = name + "/" + str(x + 1)

        # Determine type of content (book-like content needs to be redone)
        '''if type(content_data) is dict: # Book-like content
            content = content_data["abstract"]
            content += "\n\n[ Table of Contents ]"

            # Add remaining sections
            for y in range(0, len(content_data["pages"])):
                print("Publishing subpage ", y)
                subpage_data = content_data["pages"][y]

                # Add subpage URL to table of contents
                subpage_url = article_url + "/" + str(y + 1)
                subpage_list_line = "/" + subpage_url + " \t" + subpage_data["title"]
                content += "\n" + subpage_list_line

                # Write on subpage
                subpage_content = article_header + "\n"
                # Add previous URL
                if y > 0:
                    subpage_content += "\nPrev: [/" + article_url + "/" + str(y) + "]"
                # Add next URL
                if y < len(content_data):
                    subpage_content += "\nNext: [/" + article_url + "/" + str(y + 2) + "]"
                subpage_content += "\n═════════════════════════════"
                subpage_content += "\n\n" + item["title"] + "\n" + subpage_data["title"]
                subpage_content += "\n\n" + subpage_data["content"]

                # Post to article subpage
                ett.post_async(subpage_url, subpage_content)
        else: # Article-like content
            content = content_data'''
        content = content_data

        # Add information source in parentheses to content start
        # (only if titles are not authored)
        if not authored_titles:
            content = "(" + item["author"] + ") " + content

        # Post article page content
        page_content = ""
        page_content += article_header # Add header
        page_content += "\n\n" + item["title"] + "\nAuthor: " + item["author"] + "\nDate: " + item["date"] # Add article metadata
        # page_content += "\n\n" + get_article_with_ad(content, ad, get_article_start_end(content)) # Add article content with ads
        page_content += "\n\n" + content # Add article content without ads
        page_content += "\n\n═════════════════════════════"
        page_content += "\n\nCite this article:\n" + item["author"] + ". (" + item["date"] + "). \"" + item["title"] + "\". Retrieved from /" + article_url
        ett.post_async(article_url, page_content) # Post to article page

        # Add information to root page
        article_list_line = "/" + article_url + " \t" 
        if authored_titles: # Put author names before article titles
            article_list_line += item["author"] + ": "
        article_list_article_title = (item["title"] + (" (" + item["date"] + ")" if len(item["date"]) > 0 else ""))[:root_title_length]
        article_list_line += article_list_article_title
        article_list = "\n" + article_list_line + article_list
        
        if (x == length - 1 and show_featured == True):
            featured += "\n\n═════════════════════════════\n" + item["title"] + " (" + item["date"] + ")" + "\n\n" + get_article_start(content) + "\n\n═════════════════════════════"

    # Post root page content
    root_content = header + featured + "\n\n══ Articles ══" + article_list + "\n\n═════════════════════════════\nProvided by ETT News – tikolu.net/edit/news"
    ett.post(name, root_content)
    ett.post("backup/" + name, root_content)

    # [remove] Post to backup
    #backup_info = ett.get(name + "/i/backup").strip()
    #if len(backup_info) != 0:
    #    extra_backup_list = backup_info.split("\n")
    #    for x in extra_backup_list:
    #        ett.post(x, root_content)

# adds an article to a page without updating the root page
# name: root page
# has_date: if True, the date will automatically be chosen. otherwise, it will display the date value of "has_date"
def add(name, title, author, has_date, content):
    data = get_enn(get_enn_url(name))
    datestr = ""
    if has_date == True:
        date = datetime.datetime.now()
        datestr = date.strftime("%d") + " " + date.strftime("%B") + " " + date.strftime("%Y")
    elif has_date != False:
        datestr = has_date
    data["art"].append({"title": title, "author": author, "date": datestr, "content": content})
    post_enn(name + "/json", data) # [remove]
    post_enn(get_enn_url(name), data)

# for test
def get_dates(name):
    string = ""
    data = get_enn(get_enn_url(name))
    length = len(data["art"])
    for x in range(0, length):
        string = string + data["art"][x]["date"] + "\n"
    return string
