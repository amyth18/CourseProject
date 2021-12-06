CWD="$(pwd)"
docker run --name mongodb -d -v "$CWD"/mongodb:/data/db -p 27017:27017 --network maximus mongo
