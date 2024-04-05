FROM openjdk:17
ARG WAR_FILE=build/*.war
COPY ${WAR_FILE} app.war
ENTRYPOINT ["java","-jar","/app.war"]
