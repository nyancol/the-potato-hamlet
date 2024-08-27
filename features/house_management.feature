Feature: House creation
  As a new user
  I want to create a house
  So I can start personalizing my household's house

  Scenario: Successfully create a house
    Given A user named "user0" exists
    And The "user0" belongs to a household named "hh_0"
    And A hamlet named "hl_0" exists
     When I create a house named "house_0" belonging to the household "1" in the hamlet "1"
     Then I should receive a confirmation of a successful creation
     And A house named "house_0" should exist
     And A world item linked to a house "house_0" should exist

  Scenario: Successfully fetch a house
    Given A household named "hh_0" exists
    And A hamlet named "hl_0" exists
     And A house named "house_0" belonging to the household "1" in the hamlet "1" exists
     When I fetch the house of id "1"
     Then I should receive a house id, item_id, household_id and hamlet_id

