activate_this = "/root/diagtool/bin/activate_this.py"
with open(activate_this) as f:
        code = compile(f.read(), activate_this, 'exec')
        exec(code, dict(__file__=activate_this))
        
SQL_QUERIES_LIMIT_FOR_PERFORMANCE_INSIGHTS = 5
