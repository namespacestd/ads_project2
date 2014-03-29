
import json
import urllib

def relevant_mid(mid):
    mid_url = mid_query_url + mid + '?key=' + api_key
    mid_response = json.loads(urllib.urlopen(mid_url).read())

    types = mid_response['property']['/type/object/type']['values']
    relevant_types = []

    for t in types:
        type_id = t['id']
        if type_id in relevant_topics:
            relevant_types.append(type_id)

    return mid_response, set(relevant_types)

def get_property_value(mid_json, prop, value):
    try:
        #print mid_json['property'][prop]['values'][0][value]
        return mid_json['property'][prop]['values'][0][value]
    except:
        return None

def get_subproperty_node_text(node, index, field):
    try:
        return node['property'][index]['values'][0][field]
    except:
        return None

api_key = "AIzaSyAbDNBtuCvq3YkvcK4xaUrqnTtaBTMl-4M"
query = 'Bill Gates'
service_url = 'https://www.googleapis.com/freebase/v1/search'
mid_query_url = 'https://www.googleapis.com/freebase/v1/topic'
params = {
        'query': query,
        'key': api_key
}



relevant_topics = {
    '/people/person' : 'Person',
    '/book/author' : 'Author',
    '/film/actor' : 'Actor',
    '/tv/tv_actor' : 'Actor',
    '/organization/organization_founder' : 'BusinessPerson',
    '/business/board_member' : 'BusinessPerson',
    '/sports/sports_league' : 'League',
    '/sports/sports_team' : 'SportsTeam',
    '/sports/professional_sports_team' : 'SportsTeam'
}


url = service_url + '?' + urllib.urlencode(params)
response = json.loads(urllib.urlopen(url).read())
first_relevant = None
associated_topics = []
associated_json = None

for result in response['result']:
    current_mid = result['mid']
    stuff = relevant_mid(current_mid)

    associated_topics = list(stuff[1])
    associated_json = stuff[0]

    if associated_topics:
        first_relevant = current_mid
        break

print associated_topics

if first_relevant:
    for topic in associated_topics:
        if topic == '/people/person':
            person_name = get_property_value(associated_json, '/type/object/name', 'text')
            person_dob = get_property_value(associated_json, '/people/person/date_of_birth', 'text')
            person_pob = get_property_value(associated_json, '/people/person/place_of_birth', 'text')
            person_date_of_death = get_property_value(associated_json, '/people/deceased_person/date_of_death', 'text')
            person_cause_of_death = get_property_value(associated_json, '/people/deceased_person/cause_of_death', 'text')
            person_place_of_death = get_property_value(associated_json, '/people/deceased_person/place_of_death', 'text')
            
            sibling_names = []
            try:
                siblings = associated_json['property']['/people/person/sibling_s']['values']
                for sibling in siblings:                    
                    sibling_names.append(sibling['property']['/people/sibling_relationship/sibling']['values'][0]['text'].encode('ascii', 'ignore'))
            except:
                pass

            spouse_details = []
            try:
                spouses = associated_json['property']['/people/person/spouse_s']['values']
                for spouse in spouses:
                    spouse_name = spouse['property']['/people/marriage/spouse']['values'][0]['text']
                    spouse_date_to = spouse['property']['/people/marriage/to']['values']
                    spouse_date = spouse['property']['/people/marriage/from']['values'][0]['text'] + " - " + ('now' if spouse_date_to == [] else spouse_date_to[0]['text'] )
                    spouse_location = spouse['property']['/people/marriage/location_of_ceremony']['values'][0]['text']
                    spouse_details.append((spouse_name + " (" + spouse_date + ") @ " + spouse_location).encode('ascii', 'ignore'))
            except:
                pass

            description = get_property_value(associated_json, "/common/topic/description", 'value')

            print person_name
            print person_dob
            print person_pob
            print person_date_of_death
            print person_cause_of_death
            print person_place_of_death
            print sibling_names
            print spouse_details
            print description
        elif topic == '/book/author':
            books_written = []

            try:
                books = associated_json['property']['/book/author/works_written']['values']
                for book in books:
                    books_written.append(book['text'].encode('ascii', 'ignore'))
            except:
                pass

            book_works = []
            try:
                books = associated_json['property']['/book/book_subject/works']['values']
                for book in books:
                    book_works.append(book['text'].encode('ascii', 'ignore'))
            except:
                pass

            influenced_people = []
            try:
                people = associated_json['property']['/influence/influence_node/influenced']['values']
                for person in people:
                    influenced_people.append(person['text'].encode('ascii', 'ignore'))
            except:
                pass

            influenced_by_people = []
            try: 
                people = associated_json['property']['/influence/influence_node/influenced_by']['values']
                for person in people:
                    influenced_by_people.append(person['text'].encode('ascii', 'ignore'))
            except:
                pass

            print books_written
            print book_works
            print influenced_people
            print influenced_by_people
        elif topic == '/organization/organization_founder':
            organizations_founded = []
            try:
                organizations = associated_json['property']['/organization/organization_founder/organizations_founded']['values']
                for organization in organizations:
                    organizations_founded.append(organization['text'].encode('ascii', 'ignore'))
            except:
                pass

            print organizations_founded
        elif topic == '/business/board_member':
            leadership_roles = []
            try:
                boards = associated_json['property']['/business/board_member/leader_of']['values']
                for board in boards:
                    position = {}
                    position['organization'] = get_subproperty_node_text(board, '/organization/leadership/organization', 'text')
                    position['role'] = get_subproperty_node_text(board, '/organization/leadership/role', 'text')
                    position['title'] = get_subproperty_node_text(board, '/organization/leadership/title', 'text')
                    date_from = get_subproperty_node_text(board, '/organization/leadership/from', 'text')
                    date_to = get_subproperty_node_text(board, '/organization/leadership/to', 'text')
                    position['dates'] = date_from + " - " + date_to
                    leadership_roles.append(position)
            except:
                pass

            board_membership = []
            try: 
                boards = associated_json['property']['/business/board_member/organization_board_memberships']['values']
                for board in boards:
                    position = {}
                    position['organization'] = get_subproperty_node_text(board, '/organization/organization_board_membership/organization', 'text')
                    position['role'] = get_subproperty_node_text(board, '/organization/organization_board_membership/role', 'text')
                    position['title'] = get_subproperty_node_text(board, '/organization/organization_board_membership/title', 'text')
                    date_from = get_subproperty_node_text(board, '/organization/organization_board_membership/from', 'text')
                    date_to = get_subproperty_node_text(board, '/organization/organization_board_membership/to', 'text')
                    position['dates'] = str(date_from) + " - " + ('now' if date_to == None else date_to)
                    board_membership.append(position)
            except:
                pass

            print leadership_roles
            print board_membership
else:
    print "No relevant queries returned."