import psycopg2
from flask import Flask, render_template, request

app = Flask(__name__)

def getConn():
    #function to retrieve the password, construct
    #the connection string, make a connection and return it.
    pwFile = open("pw.txt", "r")
    pw = pwFile.read();
    pwFile.close()
    connStr = "host='cmpstudb-01.cmp.uea.ac.uk' \
               dbname= 'uxt14awa' user='uxt14awa' password = " + pw   
    conn=psycopg2.connect(connStr)          
    return  conn
  

@app.route('/')
def home():     
    return render_template('home.html')
    

#TASK 111111111111111111111111111111111111111111111111111111111111111111111
@app.route('/addCategory', methods=['POST'])
def addCategory():

	#Declaring variables and getting the user's input
    conn=None
    id=int(request.form['categoryID'])
    name=request.form['categoryName']
    categotyType=request.form['categoryType']

    #Connection to the database and execution of SQL commands (adding a new category)
    try:                 
        conn = getConn()
        cur = conn.cursor()
        cur.execute('SET search_path to coursework')
        cur.execute('SELECT add_category(%s, %s, %s)', [id, name, categotyType])
        conn.commit()
        message = "Category added"
        return render_template('home.html', message=message)
    except Exception as e:
        return render_template('home.html', message=e)
    finally:
        if conn:
            conn.close()             


#TASK 22222222222222222222222222222222222222222222222222222222222222222
@app.route('/removeCategory', methods=['POST'])
def removeCategory():

	#Declaring variables and getting the user's input
    conn=None
    id = int(request.form['categoryID'])

    #Connection to the database and execution of SQL commands (removing a category)
    try:
    	conn=getConn()
    	cur=conn.cursor()
    	cur.execute('SET search_path to coursework')
    	cur.execute('SELECT remove_category(%s)', [id])
    	conn.commit()
    	message="Category removed"
    	return render_template('home.html', message=message)
    except Exception as e:
        return render_template('home.html', message=e)    	
    finally:
        if conn:
            conn.close()        


#TASK 333333333333333333333333333333333333333333333333333333333
@app.route('/summaryReport', methods=['GET'])
def summaryReport():

	#Declaring variables
    conn=None

	#Connection to the database and execution of SQL commands (producing a summary report)
    try:
        conn=getConn()
        cur=conn.cursor()
        cur.execute('SET search_path to coursework')
        cur.execute('SELECT Number_Of_Titles, Average_Price From summary_report_of_books UNION ALL SELECT Sum(Number_Of_Titles), Sum(Average_Price) From summary_report_of_books;')         
        colNames = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        message="Report produced"
        return render_template('table.html', message=message, rows=rows, colNames=colNames)
    except Exception as e:
        return render_template('home.html', message=e)	    
    finally:
        if conn:
            conn.close()        


#TASK 4444444444444444444444444444444444444444444444444444444444444
@app.route('/bookReport', methods=['POST'])
def bookReport():

    #Declaring variables and getting the user's input
    conn=None
    name=request.form['publisherName']

    #Connection to the database and execution of SQL commands (producing a book report)
    try:
        conn=getConn()
        cur=conn.cursor()
        cur.execute('SET search_path to coursework')    
        cur.execute("SELECT date_part('year',Orderdate) AS year, date_part('month',Orderdate) AS month, B.BookID, Title, COUNT(Title) AS total_number_of_orders, SUM(Quantity), SUM(unitSellingPrice * Quantity) AS Order_value, SUM(price * Quantity) AS retail_value FROM BOOK AS B, Shoporder AS SO, Orderline AS OL, Publisher AS P WHERE P.name=%s AND P.PublisherID = B.PublisherID AND B.BookID = OL.BookID AND OL.ShopOrderID = SO.ShopOrderID  Group BY date_part('year',Orderdate), date_part('month',Orderdate), b.bookid ORDER BY date_part('year',Orderdate), date_part('month',Orderdate)", [name]) 
        colNames = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        message="Report produced"
        return render_template('table.html', message=message, colNames=colNames, rows=rows)
    except Exception as e:
        return render_template('home.html', message=e)
    finally:
        if conn:
            conn.close()


#TASK 55555555555555555555555555555555555555555555555555
@app.route('/bookOrderHistory', methods=['POST'])            
def bookOrderHistory():

    #Declaring variables
    conn=None
    id=int(request.form['BookID'])
    
	#Connection to the database and execution of SQL commands (producing a book order history)
    try:
        conn=getConn()
        cur=conn.cursor()
        cur.execute('SET search_path to coursework')        
        query_1="SELECT OrderDate, Title, Price, UnitSellingPrice, Quantity, Quantity * UnitSellingPrice AS OrderValue, SO.Name FROM Book AS B, ShopOrder AS S, OrderLine AS O, Shop AS SO WHERE B.BookID = O.BookID AND S.ShopOrderID = O.ShopOrderID AND S.ShopID = SO.ShopID AND O.BookID = " + str(id)
        cur.execute(query_1 + "UNION SELECT  null , 'Total', null, null, SUM(quantity), SUM(Quantity * UnitSellingPrice), ' '  FROM OrderLine WHERE OrderLine.bookid = %s ORDER BY orderdate;", [id])
        colNames = [desc[0] for desc in cur.description]
        rows = cur.fetchall()        
        message="Report produced"
        return render_template('table.html', message=message, rows=rows, colNames=colNames)
    except Exception as e:
        return render_template('home.html', message=e)	    
    finally:
        if conn:
            conn.close()


#TASK 66666666666666666666666666666666666666666666666
@app.route('/repPreformanceReport', methods=['POST'])
def repPreformanceReport():
    
    #Importing the tools needed for getting the user's input
    from datetime import datetime

    #Declaring variables and getting the user's input
    conn=None                                                         
    startDate=request.form['startDate']
    startDate=datetime.strptime(startDate, '%Y-%m-%d')

    endDate=request.form['endDate'] 
    endDate=datetime.strptime(endDate, '%Y-%m-%d')

    #Checking the order of the start and end date
    if startDate < endDate:
        #Connection to the database and execution of SQL commands (produce performance report)
        try:
            conn=getConn()
            cur=conn.cursor()
            cur.execute('SET search_path to coursework')
            cur.execute('SELECT S.name AS salesrep_name, SUM(quantity) AS total_units_sold, SUM(quantity * unitsellingprice) AS total_order_value FROM (SalesRep AS S LEFT JOIN ShopOrder AS SO ON S.salesrepid = SO.salesrepid AND orderdate > %s AND orderdate < %s) LEFT JOIN OrderLine AS O ON SO.shoporderid = O.shoporderid  GROUP BY S.name ORDER BY total_order_value DESC NULLS LAST', [startDate, endDate])
            colNames = [desc[0] for desc in cur.description]
            rows = cur.fetchall() 
            message="Report produced"
            return render_template('table.html', message=message, rows=rows, colNames=colNames)
        except Exception as e:
            return render_template('home.html', message=e)
        finally:
            if conn:
                conn.close()            
    else:
        message="The order of the start and end date has been entered reversely, try the right order"
        return render_template('home.html', message=message)            


#TASK 777777777777777777777777777777777777777777777777777
@app.route('/applyDiscount', methods=['post'])
def applyDiscount():

    #Declaring variables and getting the user's input
    conn=None
    id=int(request.form['categoryID3'])
    discount=int(request.form['discount'])

    #Connection to the database and execution of SQL commands (applying discount)
    try:
        conn=getConn()
        cur=conn.cursor()
        cur.execute('SET search_path to coursework')
        cur.execute('SELECT apply_discount(%s, %s)', [id, discount])
        conn.commit()
        message="Discount applied"
        return render_template('home.html', message=message)
    except Exception as e:
        return render_template('home.html', message=e)
    finally:
        if conn:
            conn.close()

            
if __name__ == "__main__":
    app.run(debug = True)
