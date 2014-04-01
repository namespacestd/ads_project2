import json
import urllib
import sys

###########################################
# AIzaSyAbDNBtuCvq3YkvcK4xaUrqnTtaBTMl-4M
###########################################

search_api_url = 'https://www.googleapis.com/freebase/v1/search'
topic_api_url  = 'https://www.googleapis.com/freebase/v1/topic'
question_api_url = 'https://www.googleapis.com/freebase/v1/mqlread?query='

relevant_topics = {
    '/people/person'                     : 'Person',
    '/book/author'                       : 'Author',
    '/film/actor'                        : 'Actor',
    '/tv/tv_actor'                       : 'Actor',
    '/organization/organization_founder' : 'BusinessPerson',
    '/business/board_member'             : 'BusinessPerson',
    '/sports/sports_league'              : 'League',
    '/sports/sports_team'                : 'SportsTeam',
    '/sports/professional_sports_team'   : 'SportsTeam'
}

relevant_question_topics = {
    '/organization/organization'         : 'Organization',
    '/book/book'                         : 'Book',
}

#===========================================
# Queries Freebase Topic API with given mid
#===========================================
def relevant_mid(mid):
    mid_url = topic_api_url + mid + '?key=' + api_key
    mid_response = json.loads(urllib.urlopen(mid_url).read())

    types = mid_response['property']['/type/object/type']['values']
    relevant_types = []

    for t in types:
        type_id = t['id']
        if type_id in relevant_topics:
            relevant_types.append(type_id)

    return mid_response, set(relevant_types)

def relevant_question_types(mid):
    mid_url = topic_api_url + mid + '?key=' + api_key
    mid_response = json.loads(urllib.urlopen(mid_url).read())

    values = mid_response['property']['/type/object/type']['values']
    types = []

    for t in values:
        type_id = t['id']
        if type_id in relevant_question_topics:
            types.append(type_id)

    return mid_response, set(types)

#=============================================
# Returns value of property in json structure
#=============================================
def get_property_value(json, prop, val):
    try:
        return json['property'][prop]['values'][0][val]
    except:
        return ""

#========================================================================
# Queries Freebase API and returns information about top relevant result
#========================================================================
def execute_query(query, api_key):
    url = search_api_url + '?' + urllib.urlencode({ 'query': query, 'key': api_key })
    response = json.loads(urllib.urlopen(url).read())
    first_relevant = None
    associated_topics = []
    associated_json = None
    query_results = {}

    #=================================
    # Determine first relevant entity
    #=================================
    for result in response['result']:
        current_mid = result['mid']
        temp = relevant_mid(current_mid)

        associated_topics = list(temp[1])
        associated_json = temp[0]

        if associated_topics:
            first_relevant = current_mid
            break

    print associated_topics
    print first_relevant

    if first_relevant:
        for topic in associated_topics:

            #=====================
            # Entity type: Person
            #=====================
            if topic == '/people/person':

                # Name, date of birth, place of birth, place of death, date of death, cause of death
                person_name           = get_property_value(associated_json, '/type/object/name', 'text')
                person_dob            = get_property_value(associated_json, '/people/person/date_of_birth', 'text')
                person_pob            = get_property_value(associated_json, '/people/person/place_of_birth', 'text')
                person_date_of_death  = get_property_value(associated_json, '/people/deceased_person/date_of_death', 'text')
                person_cause_of_death = get_property_value(associated_json, '/people/deceased_person/cause_of_death', 'text')
                person_place_of_death = get_property_value(associated_json, '/people/deceased_person/place_of_death', 'text')
                
                # Siblings
                sibling_names = []
                try:
                    siblings = associated_json['property']['/people/person/sibling_s']['values']
                    for sibling in siblings:                    
                        sibling_names.append(sibling['property']['/people/sibling_relationship/sibling']['values'][0]['text'].encode('ascii', 'ignore'))
                except:
                    pass

                # Spouses
                spouse_details = []
                try:
                    spouses = associated_json['property']['/people/person/spouse_s']['values']
                    for spouse in spouses:
                        spouse_name     = get_property_value(spouse, '/people/marriage/spouse', 'text')
                        date_from       = get_property_value(spouse, '/people/marriage/from', 'text')
                        date_to         = get_property_value(spouse, '/people/marriage/to', 'text')
                        spouse_date     = date_from + " - " + ('now' if date_to == "" else date_to)
                        spouse_location = get_property_value(spouse, '/people/marriage/location_of_ceremony', 'text')
                        spouse_details.append((spouse_name + " (" + spouse_date + ") " + ("" if spouse_location == "" else "@ " + spouse_location)).encode('ascii', 'ignore'))
                except:
                    pass

                # Description
                description = get_property_value(associated_json, "/common/topic/description", 'value').encode('ascii', 'ignore')

                query_results['name'] = person_name
                query_results['dob'] = person_dob
                query_results['pob'] = person_pob
                print person_date_of_death
                print person_cause_of_death
                print person_place_of_death
                print sibling_names
                print spouse_details
                print description

            #=====================
            # Entity type: Author
            #=====================
            elif topic == '/book/author':

                # Books
                books_written = []
                try:
                    books = associated_json['property']['/book/author/works_written']['values']
                    for book in books:
                        books_written.append(book['text'].encode('ascii', 'ignore'))
                except:
                    pass

                # Books about author
                books_about = []
                try:
                    books = associated_json['property']['/book/book_subject/works']['values']
                    for book in books:
                        books_about.append(book['text'].encode('ascii', 'ignore'))
                except:
                    pass

                # Influenced
                influenced = []
                try:
                    people = associated_json['property']['/influence/influence_node/influenced']['values']
                    for person in people:
                        influenced.append(person['text'].encode('ascii', 'ignore'))
                except:
                    pass

                # Influenced by
                influenced_by = []
                try: 
                    people = associated_json['property']['/influence/influence_node/influenced_by']['values']
                    for person in people:
                        influenced_by.append(person['text'].encode('ascii', 'ignore'))
                except:
                    pass

                print books_written
                print books_about
                print influenced
                print influenced_by

            #====================
            # Entity type: Actor
            #====================
            elif topic == '/film/actor':

                # Films
                films_participated = []
                try:
                    films = associated_json['property']['/film/actor/film']['values']
                    for film in films:
                        film_entity = {}
                        film_entity['character'] = get_property_value(film, '/film/performance/character', 'text')
                        film_entity['film_name'] = get_property_value(film, '/film/performance/film', 'text')
                        films_participated.append(film_entity)
                except:
                    pass

                print films_participated

            #=============================
            # Entity type: BusinessPerson
            #=============================
            elif topic == '/organization/organization_founder':

                # Founded
                organizations_founded = []
                try:
                    organizations = associated_json['property']['/organization/organization_founder/organizations_founded']['values']
                    for organization in organizations:
                        organizations_founded.append(organization['text'].encode('ascii', 'ignore'))
                except:
                    pass

                print organizations_founded

            elif topic == '/business/board_member':

                # Leadership
                leadership_roles = []
                try:
                    boards = associated_json['property']['/business/board_member/leader_of']['values']
                    for board in boards:
                        position = {}
                        position['organization'] = get_property_value(board, '/organization/leadership/organization', 'text')
                        position['role']         = get_property_value(board, '/organization/leadership/role', 'text')
                        position['title']        = get_property_value(board, '/organization/leadership/title', 'text')
                        date_from                = get_property_value(board, '/organization/leadership/from', 'text')
                        date_to                  = get_property_value(board, '/organization/leadership/to', 'text')
                        position['dates']        = date_from + " - " + date_to
                        leadership_roles.append(position)
                except:
                    pass

                # Board member
                board_membership = []
                try: 
                    boards = associated_json['property']['/business/board_member/organization_board_memberships']['values']
                    for board in boards:
                        position = {}
                        position['organization'] = get_property_value(board, '/organization/organization_board_membership/organization', 'text')
                        position['role']         = get_property_value(board, '/organization/organization_board_membership/role', 'text')
                        position['title']        = get_property_value(board, '/organization/organization_board_membership/title', 'text')
                        date_from                = get_property_value(board, '/organization/organization_board_membership/from', 'text')
                        date_to                  = get_property_value(board, '/organization/organization_board_membership/to', 'text')
                        position['dates']        = str(date_from) + " - " + ('now' if date_to == "" else date_to)
                        board_membership.append(position)
                except:
                    pass

                print leadership_roles
                print board_membership

            #=====================
            # Entity type: League
            #=====================
            elif topic == '/sports/sports_league':

                # Name, championship, sport, slogan, website
                name         = get_property_value(associated_json, '/type/object/name', 'text')
                championship = get_property_value(associated_json, '/sports/sports_league/championship', 'text')
                sport        = get_property_value(associated_json, '/sports/sports_league/sport', 'text')
                slogan       = get_property_value(associated_json, '/organization/organization/slogan', 'text')
                website      = get_property_value(associated_json, '/common/topic/official_website', 'text')

                # Description
                description = get_property_value(associated_json, '/common/topic/description', 'value').encode('ascii', 'ignore')

                # Teams
                partipating_teams = []
                try:
                    teams = associated_json['property']['/sports/sports_league/teams']['values']
                    for team in teams:
                        partipating_teams.append(get_property_value(team, '/sports/sports_league_participation/team', 'text'))
                except:
                    pass

                print name
                print sport
                print slogan
                print website
                print championship
                print partipating_teams
                print description

            #=========================
            # Entity type: SportsTeam
            #=========================
            elif topic =='/sports/professional_sports_team':

                # Name
                name = get_property_value(associated_json, '/type/object/name', 'text')
                print name

            elif topic == '/sports/sports_team':

                # Name, sport, arena
                name  = get_property_value(associated_json, '/type/object/name', 'text')
                sport = get_property_value(associated_json, '/sports/sports_team/sport', 'text')
                arena = get_property_value(associated_json, '/sports/sports_team/arena_stadium', 'text')

                # Championships
                championships = []
                try: 
                    games = associated_json['property']['/sports/sports_team/championships']['values']
                    for game in games:
                        championships.append(game['text'].encode('ascii', 'ignore'))
                except:
                    pass 
                
                # Founded
                date_founded = get_property_value(associated_json, '/sports/sports_team/founded', 'text')
                
                # Leagues
                league_partipation = []
                try:
                    leagues = associated_json['property']['/sports/sports_team/league']['values']
                    for league in leagues:
                        league_partipation.append(get_property_value(league, '/sports/sports_league_participation/league', 'text').encode('ascii', 'ignore'))
                except:
                    pass

                # Locations
                team_locations = []
                try:
                    locations = associated_json['property']['/sports/sports_team/location']['values']
                    for location in locations:
                        team_locations.append(location['text'].encode('ascii', 'ignore'))
                except:
                    pass

                # Coaches
                team_coaches = []
                try:
                    coaches = associated_json['property']['/sports/sports_team/coaches']['values']
                    for coach in coaches:
                        coach_entity = {}
                        coach_entity['name']     = get_property_value(coach, '/sports/sports_team_coach_tenure/coach', 'text')
                        coach_entity['position'] = get_property_value(coach, '/sports/sports_team_coach_tenure/position', 'text')
                        date_from                = get_property_value(coach, '/sports/sports_team_coach_tenure/from', 'text')
                        date_to                  = get_property_value(coach, '/sports/sports_team_coach_tenure/to', 'text')
                        coach_entity['date']     = date_from + " - " + ('now' if date_to == "" else date_to)
                        team_coaches.append(coach_entity)
                except:
                    pass

                # Roster
                team_roster = []
                try:
                    players = associated_json['property']['/sports/sports_team/roster']['values']
                    for player in players:
                        player_entity = {}
                        player_entity['name'] = get_property_value(player, '/sports/sports_team_roster/player', 'text')
                        player_entity['position'] = []
                        try: 
                            positions = player['property']['/sports/sports_team_roster/position']['values']
                            for position in positions:
                                player_entity['position'].append(position['text'].encode('ascii', 'ignore'))
                        except:
                            pass

                        date_from = get_property_value(player, '/sports/sports_team_roster/from', 'text')
                        date_to = get_property_value(player, '/sports/sports_team_roster/to', 'text')
                        player_entity['date'] = (date_from + " - " + ('now' if date_to == "" else date_to)).encode('ascii', 'ignore')
                        player_entity['number'] = get_property_value(player, '/sports/sports_team_roster/number', 'text').encode('ascii', 'ignore')
                        team_roster.append(player_entity)
                except:
                    pass

                # Description
                description = get_property_value(associated_json, "/common/topic/description", 'value').encode('ascii', 'ignore')

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
        print "ERROR: No relevant queries returned."

def execute_question_query(query, api_key):
    query_tokens = query.split(" ")
    if((query_tokens[0].lower() == 'who') and (query_tokens[1].lower() == 'created')):
        query_tokens[-1] = query_tokens[-1].replace("?", "")
        target = " ".join(query_tokens[2:])

        query_author = [{
            "/book/author/works_written": [{
                    "a:name": [],
                    "name~=": target
                }],
                "id": [],
                "name": [],
                "type": "/book/author"
        }]

        authors = {}
        question_url = question_api_url + str(query_author)
        response = json.loads(urllib.urlopen(question_url.replace("'", '"')).read())

        for element in response["result"]:
            author = element["name"][0].encode('ascii', 'ignore')
            titles = []
            for title in element["/book/author/works_written"]:
                titles.append(title["a:name"][0].encode('ascii', 'ignore'))
            authors[author] = titles

        query_organization = [{
            "/organization/organization_founder/organizations_founded": [{
                    "a:name": [],
                    "name~=": target
                }],
                "id": [],
                "name": [],
                "type": "/organization/organization_founder"
        }]

        founders = {}
        question_url = question_api_url + str(query_organization)
        response = json.loads(urllib.urlopen(question_url.replace("'", '"')).read())

        for element in response["result"]:
            founder = element["name"][0].encode('ascii', 'ignore')
            organizations = []
            for title in element["/organization/organization_founder/organizations_founded"]:
                organizations.append(title["a:name"][0].encode('ascii', 'ignore'))
            founders[founder] = organizations

        return authors, founders

    else:
        print "ERROR: Invalid question given."

#==========================
# Displays argument syntax
#==========================
def show_usage():
    print "\nUsage:"
    print "\t1. -key <api_key> -q <query> -t [infobox|question]"
    print "\t2. -key <api_key> -f <file>  -t [infobox|question]"
    print "\t3. -key <api_key>"

#====================
# Main program logic
#====================
if(len(sys.argv) == 7):
    if(sys.argv[1] == '-key' and (sys.argv[3] == '-q' or sys.argv[3] == '-f') and sys.argv[5] == '-t' and (sys.argv[6] == 'infobox' or sys.argv[6] == 'question')):
        api_key = sys.argv[2]
        mode = sys.argv[6]

        #==============
        # Single query
        #==============
        if(sys.argv[3] == '-q'):
            if(sys.argv[6] == 'infobox'):
                query = sys.argv[4]
                execute_query(query, api_key)
            elif(sys.argv[6] == 'question'):
                query = sys.argv[4]
                authors, founders = execute_question_query(query, api_key)

                answers = []
                for key, value in authors.iteritems():
                    answers.append(key + " (as Author) created " + ' and '.join('<{0}>'.format(w) for w in value))
                for key, value in founders.iteritems():
                    answers.append(key + " (as BusinessPerson) created " + ' and '.join('<{0}>'.format(w) for w in value))
                answers.sort()

                counter = 1
                print "\n\n\n"
                for answer in answers:
                    print str(counter) + ". " + answer
                    counter+=1 
                print "\n\n\n"
        
        #===================
        # Queries from file
        #===================
        else:
            pass

    else:
        show_usage()

#===================
# Interactive shell
#===================
elif(len(sys.argv) == 2):
    if(sys.argv[1] == '-key'):
        pass
    else:
        show_usage()
else:
    show_usage()