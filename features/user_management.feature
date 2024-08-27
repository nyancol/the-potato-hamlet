Feature: User management
  As a new user
  I want to register, modify and delete my account
  So that I can access and manage my user details in the game


  Scenario Outline: Successfully register a new user
    Given I am logging in the registration page
     When I provide a <username>, <email>, <password>, <first_name> and <last_name>
     Then I should receive a confirmation of a sucessful registration

   Examples:
       | username | email           | password | first_name | last_name |
       | test1234 | test@gmail.com  | test1234 | first_name | last_name |
       | test1234 | toto@gmail.com  | test1234 | first_name | last_name |


  Scenario Outline: Unsuccessfully register a new user
    Given I am logging in the registration page
     When I provide a <username>, <email>, <password>, <first_name> and <last_name>
     Then I should receive an error "422" message

   Examples:
       | username | email    | password | first_name | last_name |
       | test1234 | testcom  | test1234 | first_name | last_name |
       | test1234 | test@gmail.com  | asdf | first_name | last_name |

  Scenario: Unsuccessful register a new user due to same exising username
    Given There is an existing user "username1" and "email1@gmail.com"
     When I provide registration values "username1" and "email2@gmail.com"
     Then I should receive an error "409" message

  Scenario: Unsuccessful register a new user due to same exising email
    Given There is an existing user "username1" and "email1@gmail.com"
     When I provide registration values "username2" and "email1@gmail.com"
     Then I should receive an error "409" message

  Scenario: Successfully fetch the details of my user
    Given I am a new user with a username "username1"
     When I fetch my user details
     Then I should receive a status code of 200 and a payload with my user id

  Scenario: Successfully delete my user
    Given I am a new user with a username "user0"
     When I delete my user with a username "user0"
     Then My user "user0" should not exist anymore

  Scenario: Unsuccessfully update email of a different user
   Given I am a new user with a username "user0"
     And I am connected with the "user0"
     And There is an existing user "username1" and "email1@gmail.com"
    When I update the user "username1" email to "test@example.com"
    Then I should get a permission error

  Scenario: Successfully update my username
    Given I am a new user with a username "user0"
     When I update my email to "test@example.com"
     Then My user should have "test@example.com" as email

  Scenario: Successfully list all the users
    Given There are "5" users
     When I fetch the list of users
     Then I should get a list of "5" users, with valid ids and usernames


 Scenario: Successfully log in with a registered user
    Given I am a registered user "user01" with a password "password01"
     When I login with my "user01" and "password01"
     When I fetch my user details
     Then I should get a valid token and username "user01"

