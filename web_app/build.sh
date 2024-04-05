cd $(dirname $0)
mkdir -p src/main/resources/static/js && \
  wget https://code.jquery.com/jquery-3.7.1.min.js -P src/main/resources/static/js/
./mvnw clean
./mvnw compile && \
  ./mvnw package -f ./pom.xml
