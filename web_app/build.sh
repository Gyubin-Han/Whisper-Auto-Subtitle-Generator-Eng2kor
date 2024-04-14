cd $(dirname $0)
mkdir -p src/main/resources/static/js && \
  wget https://code.jquery.com/jquery-3.7.1.min.js -P src/main/resources/static/js/
mkdir -p src/main/resources/static/css && \
  wget https://github.com/twbs/bootstrap/releases/download/v5.3.3/bootstrap-5.3.3-dist.zip && \
  unzip bootstrap-5.3.3-dist.zip && \
  mv -f bootstrap-5.3.3-dist/js/* src/main/resources/static/js/ && \
  mv -f bootstrap-5.3.3-dist/css/* src/main/resources/static/css/
rm -rf bootstrap-5.3.3-dist.zip bootstrap-5.3.3-dist
./mvnw clean
./mvnw compile && \
  ./mvnw package -f ./pom.xml
