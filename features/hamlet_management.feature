Feature: Hamlet management
  As a new user
  I want browse and access Hamlets
  So that I can build my house and contribute to the community


  Scenario: Successfully fetch the Potato Hamlet
    Given I am a registered user "user0" with a password "password0"
      And I am logged in with the user "user0"
     When I fetch the list of Hamlets
     Then I should get at least one hamlet

  Scenario: Successfully request access to a Hamlet
    Given I am a registered user "user0" with a password "password0"
      And I am logged in with the user "user0"
      And A hamlet named "hl_0" exists
     When I request access to the hamlet "hl_0"
     Then I should see my request being created with a status "Submitted"

  Scenario: Successfully request approval to a Hamlet access request
    Given I am a registered user "user0" with a password "password0"
      And I am logged in with the user "user0"
      And There is an existing user "user1" and "email1@gmail.com"
      And A hamlet named "hl_0" exists
      And A hamlet access request exists from "user1" to "hl_0"
     When I approve the access request
     Then The user "user1" should have access to hamlet "hl_0"
