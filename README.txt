Martin Li (mcl2159)
Alex Dong (aqd2000)
COMS E6111 Advanced Database Systems
Project 2


===================
| Files Submitted |
===================

main.py, README.txt, transcript.txt


==============
| How to Run |
==============

Simply run main.py using the desired parameters described in the assignment. Examples:
python main.py -key <API_KEY> -q <QUERY> -t infobox
python main.py -key <API_KEY> -q <QUERY> -t question
python main.py -key <API_KEY> -f <FILE> -t infobox
python main.py -key <API_KEY> -f <FILE> -t question
    
NOTE: <QUERY> must be a single string (i.e. "Bill Gates" instead of Bill Gates)


===================
| Internal Design |
===================

Excluding the helper functions, the program is divided into several main functions:

execute_query():
    Given a query and an API key, determines the first relevant entity using the Freebase Search and Topic APIs and returns a dictionary of infobox information.

execute_question_query():
    Given a question query and an API key, queries the Freebase MQLRead API and prints answers to the question.

render_infobox():
    Given the dictionary result from execute_query(), prints the styled infobox.


    =========================================================================
    | Mapping from Freebase properties to the entity properties of interest |
    =========================================================================

    Freebase property              Property of interest                                        Tag(s) used for extraction
    ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    Person.Name:                   /type/object/name                                           'text'
    Person.Birthday:               /people/person/date_of_birth                                'text'
    Person.PlaceOfBirth:           /people/person/place_of_birth                               'text'
    Person.PlaceOfDeath:           /people/deceased_person/place_of_death                      'text'
    Person.DateOfDeath:            /people/deceased_person/date_of_death                       'text'
    Person.CauseOfDeath:           /people/deceased_person/cause_of_death                      for each element in 'values': 'text'
    Person.Siblings:               /people/person/sibling_s                                    for each element in 'values': 'property' -> '/people/sibling_relationship/sibling' -> 'text' 
    Person.Spouses:                /people/person/spouse_s                                     for each element in 'values': 'property' -> '/people/marriage/spouse' -> 'text'
    Person.Description:            /common/topic/description                                   'value'
    Author.Books:                  /book/author/works_written                                  for each element in 'values': 'text'
    Author.BooksAbout:             /book/book_subject/works                                    for each element in 'values': 'text'
    Author.Influenced:             /influence/influence_node/influenced                        for each element in 'values': 'text'
    Author.InfluencedBy:           /influence/influence_node/influenced_by                     for each element in 'values': 'text'
    Actor.Films                    /film/actor/film                                            for each element in 'values': 'property' -> '/film/performance/film' -> 'text'
                                                                                                                                        -> '/film/performance/character' -> 'text'
    BusinessPerson.Leadership:     /business/board_member/leader_of                            for each element in 'values': 'property' -> '/organization/leadership/from' -> 'text'
                                                                                                                                        -> '/organization/leadership/to' -> 'text'
                                                                                                                                        -> '/organization/leadership/organization' -> 'text'
                                                                                                                                        -> '/organization/leadership/role' -> 'text'
                                                                                                                                        -> '/organization/leadership/title' -> 'text'
    BusinessPerson.BoardMember:    /business/board_member/organization_board_memberships       for each element in 'values': 'property' -> '/organization/leadership/from' -> 'text'
                                                                                                                                        -> '/organization/leadership/to' -> 'text'
                                                                                                                                        -> '/organization/leadership/organization' -> 'text'
                                                                                                                                        -> '/organization/leadership/role' -> 'text'
                                                                                                                                        -> '/organization/leadership/title' -> 'text'
    BusinessPerson.Founded:        /organization/organization_founder/organizations_founded    for each element in 'values': 'text' 
    League.Name:                   /type/object/name                                           'text'
    League.Championship:           /sports/sports_league/championship                          'text'
    League.Sport:                  /sports/sports_league/sport                                 'text'
    League.Slogan:                 /organization/organization/slogan                           'text'
    League.Website:                /common/topic/official_website                              'text'
    League.Description:            /common/topic/description                                   'value'
    League.Teams:                  /sports/sports_league/teams                                 for each element in 'values': 'property' -> '/sports/sports_league_participation/team' -> 'text' 
    SportsTeam.Name:               /type/object/name                                           'text'
    SportsTeam.Description:        /common/topic/description                                   'value'
    SportsTeam.Sport:              /sports/sports_team/sport                                   'text'
    SportsTeam.Arena:              /sports/sports_team/arena_stadium                           'text'
    SportsTeam.Championships:      /sports/sports_team/championships                           for each element in 'values': 'text'
    SportsTeam.Coaches:            /sports/sports_team/coaches                                 for each element in 'values': 'property' -> '/sports/sports_team_coach_tenure/coach' -> 'text'
                                                                                                                                        -> '/sports/sports_team_coach_tenure/position' -> 'text'
                                                                                                                                        -> '/sports/sports_team_coach_tenure/from' -> 'text'
                                                                                                                                        -> '/sports/sports_team_coach_tenure/to' -> 'text'
    SportsTeam.Founded:            /sports/sports_team/founded                                 'text'
    SportsTeam.Leagues:            /sports/sports_team/league                                  for each element in 'values': 'property' -> '/sports/sports_league_participation/league' -> 'text'
    SportsTeam.Locations:          /sports/sports_team/location                                for each element in 'values': 'text'
    SportsTeam.Players:            /sports/sports_team/roster                                  for each element in 'values': 'property' -> '/sports/sports_team_roster/player' -> 'text'
                                                                                                                                        -> '/sports/sports_team_roster/position' -> 'text'
                                                                                                                                        -> '/sports/sports_team_roster/number' -> 'text'
                                                                                                                                        -> '/sports/sports_team_roster/from' -> 'text'
                                                                                                                                        -> '/sports/sports_team_roster/to' -> 'text'
    ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


    ===============
    | MQL Queries |
    ===============

    Books
    -------------------------------------------------------------------
    [{
        "/book/author/works_written": [{
                "a:name": [],
                "name~=": target
            }],
            "id": [],
            "name": [],
            "type": "/book/author"
    }]
    -------------------------------------------------------------------

    Organizations
    -------------------------------------------------------------------
    [{
        "/organization/organization_founder/organizations_founded": [{
                "a:name": [],
                "name~=": target
            }],
            "id": [],
            "name": [],
            "type": "/organization/organization_founder"
    }]
    -------------------------------------------------------------------


====================
| Freebase API Key |
====================

AIzaSyAbDNBtuCvq3YkvcK4xaUrqnTtaBTMl-4M
