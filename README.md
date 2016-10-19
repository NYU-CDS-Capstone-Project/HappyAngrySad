# HappyAngrySad

An Emotion Centric Content Classification System

## Description:

Current content delivery systems fail to utilize emotional statuses of users. We propose to build an emotionally intelligent content recommendation system.  Users will choose their desired emotional state and the recommendation system will deliver a piece of content with a high likelihood of eliciting the desired emotion.

## Tools:

- Emotional Classification: Affectiva API using Javascript SDK
- Web Development Framework: Flask 
- Database: NoSQL Couchdb

## Modeling
Please see modeling/README.md

Affectiva API returns a json file with the score for the list of emotions, for example: {"joy":0,"sadness":30,"disgust":0,"contempt":1,"anger":37,"fear":2,"surprise":0,"valence":-30,"engagement":52}.
 

### Building Labeled Dataset

We’re going to focus on 7 emotions: joy, sadness, disgust, contempt, anger, fear, surprise. We carefully selected 7 short videos that are likely to elicit one of these emotions. While watching the video, a user will react to the content, and we’ll capture picks in the user’s reaction. For every user we will have a json file with the scores for every emotions (Affectiva records emotions continuously). Using the users’ reaction, we plan to do SVD/cluster users into n user types.


### New Users

All new users will be asked to watch 7 ‘start’ videos to determine their user type and get personalized recommendations.


### New Content

All our content comes from YouTube videos. We utilize YouTube API to collect the associated metadata about the videos: ‘title’, ‘description’, ‘tags’, etc. Using this information, we can predict a user’s reaction to a new piece of content based on the user’s type. Our model along with the prediction will show how confident it is. To grow our labeled data efficiently, we will show a user not only videos that our model predicts the user will like, but also videos our model is not confident about. So, we will alter between maximizing users’ experience and growing the label data.
