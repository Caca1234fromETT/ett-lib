ETTNEWS_KEY = "pcu272/enn/"
# ETTNEWS_KEY should be correct otherwise you'll have an error

import json
import ett
import datetime

plugins = {}

def use_plugin_local(name):
    plugins[name] = __import__(name)

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

def get_article_property_local(article_data, key, placeholder):
    if key in article_data:
        return article_data[key]
    return placeholder

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

def format_content(content_data, content_type):
    if content_type == None: # raw text
        return content_data
    else:
        if content_type in plugins:
            return plugins[content_type].format(content_data)
        return "[Error 4]"

def list_articles(name, num = 20, root_title_length = 50, show_featured = False, authored_titles = False):
    # Get JSON data
    data = get_enn(get_enn_url(name))
    length = len(data["art"])
    header = get_data_string_local(data, "rootHeader", "/" + name)
    article_header = get_data_string_local(data, "articleHeader", "Article")
    separator= get_data_string_local(data, "separator", "═════════════════════════════")
    ads = get_data_string_local(data, "ads", ["[Error 3]"])
    ad = ads[int(datetime.datetime.now().strftime("%d")) % len(ads)]

    # Get start index
    start_index = max(0, length - num)

    # Process articles
    featured = ""
    article_list = ""
    for x in range(start_index, length):
        item = data["art"][x]
        article_url = name + "/" + str(x + 1)
        content_data = get_article_property_local(item, "content", "[Error 1]")
        content_type = get_article_property_local(item, "type", None) # Get article type or None
        content = format_content(content_data, content_type)

        # Get article metadata
        title = get_article_property_local(item, "title", "[Error 2]")
        author = get_article_property_local(item, "author", "Anonymous")
        date = get_article_property_local(item, "date", None)
        modification_date = get_article_property_local(item, "modif_date", None)

        # Add information source in parentheses to content start
        # (only if titles are not authored)
        if not authored_titles:
            content = "(" + author + ") " + content

        # Post article page content
        page_content = ""
        page_content += article_header # Add header
        page_content += "\n\n" + title # Add article metadata
        page_content += "\nAuthor: " + author
        if date != None:
            page_content += "\nDate: " + date # Add article creation date
        if modification_date != None:
            page_content += "\nLast modification: " + date # Add article modification date
        page_content += "\n\n" + content # Add article content
        page_content += "\n\n" + separator
        page_content += "\n\nCite this article:\n" + author + ". (" + (date if date != None else "n.d.") + "). \"" + title + "\". Retrieved from /" + article_url
        ett.post_async(article_url, page_content) # Post to article page

        # Add information to root page
        article_list_line = "/" + article_url + " \t" 
        if authored_titles: # Put author names before article titles
            article_list_line += author + ": "
        article_list_article_title = (title + (" (" + date + ")" if len(date) != None else ""))[:root_title_length]
        article_list_line += article_list_article_title
        article_list = "\n" + article_list_line + article_list
        
        if (x == length - 1 and show_featured == True):
            featured += "\n\n" + separator + "\n" + title + (" (" + date + ")" if len(date) != None else "") + "\n\n" + get_article_start(content) + "\n\n" + separator

    # Post root page content
    root_content = header + featured + "\n\n══ Articles ══" + article_list + "\n\n" + separator + "\nProvided by ETT News – tikolu.net/edit/news"
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
def add(name, title, author, has_date=None, content="", content_type=None):
    data = get_enn(get_enn_url(name))
    datestr = ""
    if has_date == True:
        date = datetime.datetime.now()
        datestr = date.strftime("%d") + " " + date.strftime("%B") + " " + date.strftime("%Y")
    else:
        datestr = has_date
        
    item = {"title": title, "author": author, "date": datestr, "content": content, "type": content_type}
    item = {k: v for k, v in item.items() if v}
    data["art"].append(item)
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
