echo "Update Linux"
sudo apt update

echo "Install Linux Ubuntu libs"
sudo apt install python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools python3-venv
echo "Install Redis"
sudo apt install redis-server
echo "Install PostgreSQL"
sudo apt -y install postgresql

echo "Installing dependencies"
if ! [ -d venv/ ]; then
python3 -m venv venv
fi
venv/bin/pip install -r requirements.txt
venv/bin/python manage.py collectstatic

echo "Creating systemd instance for backend"
rm /etc/systemd/system/jobbit-backend.service
cp /home/jobbit-backend/systemd/jobbit-backend.service /etc/systemd/system/
systemctl enable jobbit-backend.service
systemctl start jobbit-backend.service

echo "Setting nginx config"
rm /etc/nginx/sites-enabled/jobbit.conf
rm /etc/nginx/sites-available/jobbit.conf
cp /home/jobbit-backend/nginx/jobbit.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/jobbit.conf /etc/nginx/sites-enabled
sudo systemctl reload nginx
sudo systemctl restart nginx

echo "Build finished"