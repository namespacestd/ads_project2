import json
import urllib
import sys

###########################################
# AIzaSyAbDNBtuCvq3YkvcK4xaUrqnTtaBTMl-4M
###########################################

search_api_url   = 'https://www.googleapis.com/freebase/v1/search'
topic_api_url    = 'https://www.googleapis.com/freebase/v1/topic'
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

table_row = " -------------------------------------------------------------------------------------------------- "

#================================================================================
# Queries Freebase Search API and returns node and type information of given mid
#================================================================================
def relevant_mid(mid):
    mid_url = topic_api_url + mid + '?key=' + api_key
    mid_response = json.loads(urllib.urlopen(mid_url).read())

    types = mid_response['property']['/type/object/type']['values']
    relevant_types = []
    relevant_entities = []

    for t in types:
        type_id = t['id']
        if type_id in relevant_topics:
            relevant_types.append(type_id)
            relevant_entities.append(relevant_topics[type_id])

    return mid_response, set(relevant_types), set(relevant_entities)

#============================================================
# Returns value of given property parsed from JSON structure
#============================================================
def get_property_value(json, prop, val):
    try:
        return json['property'][prop]['values'][0][val]
    except:
        return ""

#==========================================================================
# Queries Freebase Topic API and returns infobox about top relevant result
#==========================================================================
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
            query_results['relevant_entities'] = list(temp[2])
            break

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
                        spouse_date     = ('' if date_from == "" else (date_from + " - " + ('now' if date_to == "" else date_to)))
                        spouse_location = get_property_value(spouse, '/people/marriage/location_of_ceremony', 'text')
                        spouse_details.append((spouse_name + " (" + spouse_date + ") " + ("" if spouse_location == "" else "@ " + spouse_location)).encode('ascii', 'ignore'))
                except:
                    pass

                # Description
                description = get_property_value(associated_json, "/common/topic/description", 'value').encode('ascii', 'ignore')

                query_results['name'] = person_name
                query_results['dob'] = person_dob
                query_results['pob'] = person_pob
                query_results['dod'] = person_date_of_death
                query_results['cod'] = person_cause_of_death
                query_results['pod'] = person_place_of_death
                query_results['sibling_names'] = sibling_names
                query_results['spouse_details'] = spouse_details
                query_results['description'] = description

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

                query_results['books_written'] = books_written
                query_results['books_about'] = books_about
                query_results['influenced'] = influenced
                query_results['influenced_by'] = influenced_by

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

                query_results['films_participated'] = films_participated

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

                query_results['organizations_founded'] = organizations_founded

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
                        position['dates']        = ('' if date_from == '' else (str(date_from) + " - " + ('now' if date_to == "" else date_to)))
                        board_membership.append(position)
                except:
                    pass

                query_results['leadership_roles'] = leadership_roles
                query_results['board_membership'] = board_membership

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

                query_results['name'] = name
                query_results['sport'] = sport
                query_results['slogan'] = slogan
                query_results['website'] =  website
                query_results['championship'] = championship
                query_results['partipating_teams'] = partipating_teams
                query_results['description'] = description

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
                league_participation = []
                try:
                    leagues = associated_json['property']['/sports/sports_team/league']['values']
                    for league in leagues:
                        league_participation.append(get_property_value(league, '/sports/sports_league_participation/league', 'text').encode('ascii', 'ignore'))
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

                query_results['name'] = name
                query_results['sport'] = sport
                query_results['arena'] = arena
                query_results['championships'] = championships
                query_results['date_founded'] = date_founded
                query_results['league_participation'] = league_participation
                query_results['team_locations'] = team_locations
                query_results['team_coaches'] = team_coaches
                query_results['team_roster'] = team_roster
                query_results['description'] = description
        return query_results

    else:
        print "ERROR: No relevant queries returned."

#=========================================================
# Queries Freebase MQLRead API and answers query question
#=========================================================
def execute_question_query(query, api_key):
    query_tokens = query.split(" ")
    if query_tokens[0].lower() == 'who' and query_tokens[1].lower() == 'created':
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

        answers = []
        for key, value in authors.iteritems():
            answers.append(key + " (as Author) created " + ' and '.join('<{0}>'.format(w) for w in value))
        for key, value in founders.iteritems():
            answers.append(key + " (as BusinessPerson) created " + ' and '.join('<{0}>'.format(w) for w in value))
        answers.sort()

        counter = 1
        print "\n\n"
        for answer in answers:
            print str(counter) + ". " + answer
            counter+=1 
        print "\n\n"

    else:
        print "ERROR: Invalid question given."

def get_styled_string(string, length, centered, overflow):
    string_length = len(string)
    if(string_length > length):
        if overflow == False:
            return ' ' + string[0:length-6] + '...'
        else:
            newlined = ''
            currentIndex = 0
            while(currentIndex + length < string_length):
                newlined += ' ' + string[currentIndex:currentIndex+length-4] + ' \n'
                currentIndex += length-4
            len_difference = length + currentIndex -string_length-3
            newlined += ' ' + string[currentIndex:] + (' '*(len_difference)) + ''
            return newlined
    else:
        if centered:
            len_difference = length-string_length-2
            return '' + (' '*(len_difference/2)) + string + (' '*(len_difference/2)) + ''
        else:
            len_difference = length-string_length-3
            return ' ' + string + (' '*(len_difference)) + ''


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
if len(sys.argv) == 7:
    if sys.argv[1] == '-key' and (sys.argv[3] == '-q' or sys.argv[3] == '-f') and sys.argv[5] == '-t' and (sys.argv[6] == 'infobox' or sys.argv[6] == 'question'):
        api_key = sys.argv[2]
        mode = sys.argv[6]

        #==============
        # Single query
        #==============
        if sys.argv[3] == '-q':
            query = sys.argv[4]

            # Infobox
            if mode == 'infobox':
                query_results = execute_query(query, api_key)

                query_title = query + '(' + ', '.join(query_results['relevant_entities']) +')'
                print table_row
                print '|' + get_styled_string(query_title, len(table_row), True, False) + '|'
                print table_row
                print '| Name:          ' + get_styled_string(query_results.get('name'), len(table_row)-17, False, False).replace('\n', ' |\n|                ') + ' |'
                print table_row
                print '| Birthday:      ' + get_styled_string(query_results['dob'], len(table_row)-17,  False, False).replace('\n', ' |\n|                ') + ' |'
                print table_row
                print '| Place of Birth:' + get_styled_string(query_results['pob'], len(table_row)-17,  False, False).replace('\n', ' |\n|                ') + ' |'
                print table_row
                print '| Descriptions:  ' + get_styled_string(query_results['description'].replace('\n', ' '), len(table_row)-16,  False, True).replace('\n', '|\n|                ') + '|'
                print table_row
                print '| Siblings:      ' + get_styled_string(', '.join(query_results['sibling_names']), len(table_row)-17,  False, False).replace('\n', ' |\n|                ') + ' |'
                print table_row
                print '| Spouses:       ' + get_styled_string(', '.join(query_results['spouse_details']), len(table_row)-17,  False, True).replace('\n', ' |\n|                ') + ' |'
                print table_row
                print '| Books:         ' + get_styled_string(', '.join(query_results['books_written']), len(table_row)-17,  False, True).replace('\n', ' |\n|                ') + ' |'
                print table_row
                print '| Books About:   ' + get_styled_string(', '.join(query_results['books_about']), len(table_row)-17,  False, True).replace('\n', ' |\n|                ') + ' |'
                print table_row
                print '| Influenced:    ' + get_styled_string(', '.join(query_results['influenced']), len(table_row)-17,  False, True).replace('\n', ' |\n|                ') + ' |'
                print table_row
                print '| Founded:       ' + get_styled_string(', '.join(query_results['organizations_founded']), len(table_row)-17,  False, True).replace('\n', ' |\n|                ') + ' |'
                print table_row

                leadership_roles = query_results.get('leadership_roles')
                if leadership_roles:
                    print '| Leadership:    |' + get_styled_string('Organization', 26, True, False) + '|' +  get_styled_string('Role', 18, True, False) + '|' + get_styled_string('Title', 21, True, False) + '|' + get_styled_string('From-To', 22, True, False) + '|'
                    print '|                ----------------------------------------------------------------------------------'
                    for leadership_role in leadership_roles:
                        print '|                |' + get_styled_string(leadership_role['organization'], 25, False, False) + ' |' +  get_styled_string(leadership_role['role'], 18, False, False) + '|' + get_styled_string(leadership_role['title'], 21, False, False) + '|' + get_styled_string(leadership_role['dates'], 21, False, False) + '|'
                    print table_row
                board_membership = query_results.get('board_membership')
                if board_membership:
                    print '| Board Member:  |' + get_styled_string('Organization', 26, True, False) + '|' +  get_styled_string('Role', 18, True, False) + '|' + get_styled_string('Title', 21, True, False) + '|' + get_styled_string('From-To', 22, True, False) + '|'
                    print '|                ----------------------------------------------------------------------------------'
                    for leadership_role in board_membership:
                        print '|                |' + get_styled_string(leadership_role['organization'], 25, False, False) + ' |' +  get_styled_string(leadership_role['role'], 18, False, False) + '|' + get_styled_string(leadership_role['title'], 21, False, False) + '|' + get_styled_string(leadership_role['dates'], 21, False, False) + '|'
                    print table_row
                    #if('Person' in query_results['relevant_entities']):



            # Question
            elif mode == 'question':
                execute_question_query(query, api_key)
        
        #===================
        # Queries from file
        #===================
        else:
            filename = sys.argv[4]
            try:
                f = open(filename)

                # Infobox
                if mode == 'infobox':
                    for query in f:
                        execute_query(query, api_key)

                # Question
                else:
                    for query in f:
                        execute_question_query(query, api_key)

            except IOError:
                print "ERROR: File error."

    else:
        show_usage()

#===================
# Interactive shell
#===================
elif len(sys.argv) == 3:
    if sys.argv[1] == '-key':
        api_key = sys.argv[2]
        while(True):
            query = raw_input('Enter query or question: ')
            query_words = query.split(' ')

            if len(query_words) > 2:
                if query_words[0].lower() == 'who' and query_words[1].lower() == 'created':
                    execute_question_query(query, api_key)
                else:
                    execute_query(query, api_key)
            else:
                execute_query(query, api_key)
    else:
        show_usage()
else:
    show_usage()