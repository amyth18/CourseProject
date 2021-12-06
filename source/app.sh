CWD="$(pwd)"

echo "Starting MongoDB ..."
docker run --name mongodb -d -v "$CWD"/mongodb:/data/db -p 27017:27017 --network maximus mongo
echo "Sucessfully started MongoDB."

sleep 3

echo "Starting application ..."
docker run --name maximus -d -p 8080:8080 --network maximus maximus:1.0 
echo "Sucessfully started application."
echo "Use: http://localhost:8080"

