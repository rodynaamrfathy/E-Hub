# make sure your work is saved somewhere!
rm -rf node_modules
echo "node_modules/" >> .gitignore
git add .gitignore
git commit -m "add gitignore"

# reset branch to match remote (removes bad commits)
git fetch origin
git reset --soft origin/waste-management-recycling-guidance

# recommit only safe files
git add .
git commit -m "Clean branch without node_modules"
git push origin waste-management-recycling-guidance --force
