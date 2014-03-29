
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
        return ""

def get_subproperty_node_text(node, index, field):
    try:
        return node['property'][index]['values'][0][field]
    except:
        return ""

api_key = "AIzaSyAbDNBtuCvq3YkvcK4xaUrqnTtaBTMl-4M"
query = 'N.Y. Knicks'
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
print first_relevant

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
                    spouse_name = get_subproperty_node_text(spouse, '/people/marriage/spouse', 'text')
                    date_from = get_subproperty_node_text(spouse, '/people/marriage/from', 'text')
                    date_to = get_subproperty_node_text(spouse, '/people/marriage/to', 'text')
                    spouse_date = date_from + " - " + ('now' if date_to == "" else date_to)
                    spouse_location = get_subproperty_node_text(spouse, '/people/marriage/location_of_ceremony', 'text')
                    spouse_details.append((spouse_name + " (" + spouse_date + ") " + ("" if spouse_location == "" else "@ " + spouse_location)).encode('ascii', 'ignore'))
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
                    position['dates'] = str(date_from) + " - " + ('now' if date_to == "" else date_to)
                    board_membership.append(position)
            except:
                pass

            print leadership_roles
            print board_membership
        elif topic == '/film/actor':
            films_participation = []
            try:
                films = associated_json['property']['/film/actor/film']['values']
                for film in films:
                    film_entity = {}
                    film_entity['character'] = get_subproperty_node_text(film, '/film/performance/character', 'text')
                    film_entity['film_name'] = get_subproperty_node_text(film, '/film/performance/film', 'text')
                    films_participation.append(film_entity)
            except:
                pass
            print films_participation
        elif topic == '/sports/sports_league':
            name = get_property_value(associated_json, '/type/object/name', 'text')
            sport = get_property_value(associated_json, '/sports/sports_league/sport', 'text')
            slogan = get_property_value(associated_json, '/organization/organization/slogan', 'text')
            website = get_property_value(associated_json, '/common/topic/official_website', 'text')
            championship = get_property_value(associated_json, '/sports/sports_league/championship', 'text')

            partipating_teams = []
            try:
                teams = associated_json['property']['/sports/sports_league/teams']['values']
                for team in teams:
                    partipating_teams.append(get_subproperty_node_text(team, '/sports/sports_league_participation/team', 'text'))
            except:
                pass

            description = get_property_value(associated_json, '/common/topic/description', 'value')

            print name
            print sport
            print slogan
            print website
            print championship
            print partipating_teams
            print description
        elif topic =='/sports/professional_sports_team':
            name = get_property_value(associated_json, '/type/object/name', 'text')
            print name

        elif topic == '/sports/sports_team':
            name = get_property_value(associated_json, '/type/object/name', 'text')
            sport = get_property_value(associated_json, '/sports/sports_team/sport', 'text')
            arena = get_property_value(associated_json, '/sports/sports_team/arena_stadium', 'text')

            championships = []
            try: 
                games = associated_json['property']['/sports/sports_team/championships']['values']
                for game in games:
                    championships.append(game['text'].encode('ascii', 'ignore'))
            except:
                pass 
            
            date_founded = get_property_value(associated_json, '/sports/sports_team/founded', 'text')
            league_partipation = []

            try:
                leagues = associated_json['property']['/sports/sports_team/league']['values']
                for league in leagues:
                    league_partipation.append(get_subproperty_node_text(league, '/sports/sports_league_participation/league', 'text').encode('ascii', 'ignore'))
            except:
                pass

            team_locations = []

            try:
                locations = associated_json['property']['/sports/sports_team/location']['values']
                for location in locations:
                    team_locations.append(location['text'].encode('ascii', 'ignore'))
            except:
                pass

            team_coaches = []

            try:
                coaches = associated_json['property']['/sports/sports_team/coaches']['values']
                for coach in coaches:
                    coach_entity = {}
                    coach_entity['name'] = get_subproperty_node_text(coach, '/sports/sports_team_coach_tenure/coach', 'text')
                    coach_entity['position'] = get_subproperty_node_text(coach, '/sports/sports_team_coach_tenure/position', 'text')
                    date_from = get_subproperty_node_text(coach, '/sports/sports_team_coach_tenure/from', 'text')
                    date_to = get_subproperty_node_text(coach, '/sports/sports_team_coach_tenure/to', 'text')
                    coach_entity['date'] = date_from + " - " + ('now' if date_to == "" else date_to)
                    team_coaches.append(coach_entity)
            except:
                pass

            team_roster = []

            try:
                players = associated_json['property']['/sports/sports_team/roster']['values']
                for player in players:
                    player_entity = {}
                    player_entity['name'] = get_subproperty_node_text(player, '/sports/sports_team_roster/player', 'text')
                    player_entity['position'] = []
                    try: 
                        positions = player['property']['/sports/sports_team_roster/position']['values']
                        for position in positions:
                            player_entity['position'].append(position['text'].encode('ascii', 'ignore'))
                    except:
                        pass

                    date_from = get_subproperty_node_text(player, '/sports/sports_team_roster/from', 'text')
                    date_to = get_subproperty_node_text(player, '/sports/sports_team_roster/to', 'text')
                    player_entity['date'] = (date_from + " - " + ('now' if date_to == "" else date_to)).encode('ascii', 'ignore')
                    player_entity['number'] = get_subproperty_node_text(player, '/sports/sports_team_roster/number', 'text').encode('ascii', 'ignore')
                    team_roster.append(player_entity)
            except:
                pass

            description = get_property_value(associated_json, "/common/topic/description", 'value')

            print name
            print sport
            print arena
            print championships
            print date_founded
            print league_partipation
            print team_locations
            print team_coaches
            print team_roster
            print description


else:
    print "No relevant queries returned."