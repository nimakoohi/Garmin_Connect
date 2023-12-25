import mysql.connector

def avg_db_garmin(db, res_Speed, res_hr, res_cd, res_al):
    find_total_km = "SELECT Distance AS row_count FROM ActivityData ORDER BY id DESC LIMIT 1;"

    db.cursor.execute(find_total_km)
    total_km_result = db.cursor.fetchone()[0]

    if total_km_result:
        total_km = round(total_km_result/1000)
        total_km_extra = total_km_result - (total_km*1000)
    else:
        print("Failed to retrieve Total km.")

    find_total_km = '''SELECT Distance AS row_count FROM ActivityData
    ORDER BY id DESC LIMIT 1'''

    db.cursor.execute(find_total_km)
    total_km_result = round(db.cursor.fetchone()[0])
    
    try:
        for find_another_km in range(0, total_km):
            another_km = f'''
            SELECT CONCAT(
            LPAD(EXTRACT(MINUTE FROM SEC_TO_TIME(AVG(TIME_TO_SEC(Speed)))), 2, '0'),
            ':',
            LPAD(EXTRACT(SECOND FROM SEC_TO_TIME(AVG(TIME_TO_SEC(Speed)))), 2, '0')
            ) AS average_speed
            FROM activitydata
            WHERE Distance BETWEEN {find_another_km}000 AND {find_another_km+1}000
            ORDER BY id DESC
            LIMIT 1;
            '''
            
            db.connection.commit()
            db.cursor.execute(another_km)
            another_km = db.cursor.fetchone()[0]
            res_Speed.append(another_km)
            
            hr = f'''
            SELECT CEILING(AVG(Heart_Rate)) AS HR100 FROM activitydata
            WHERE Distance BETWEEN {find_another_km}000 AND {find_another_km+1}000 ORDER BY id DESC LIMIT 1;
            '''
            
            db.connection.commit()
            db.cursor.execute(hr)
            hr = db.cursor.fetchone()[0]
            res_hr.append(hr)
            
            cd = f'''
            SELECT CEILING(AVG(Cadance)) AS cd FROM activitydata
            WHERE Distance BETWEEN {find_another_km}000 AND {find_another_km+1}000 ORDER BY id DESC LIMIT 1;
            '''
            
            db.connection.commit()
            db.cursor.execute(cd)
            cd = db.cursor.fetchone()[0]
            res_cd.append(cd)

            al_me = f'''
            SELECT CEILING(AVG(Altitude_Meters)) AS AL_Me FROM activitydata
            WHERE Distance BETWEEN {find_another_km}000 AND {find_another_km+1}000 ORDER BY id DESC LIMIT 1;
            '''

            db.connection.commit()
            db.cursor.execute(al_me)
            al_me = db.cursor.fetchone()[0]
            res_al.append(al_me)

        if total_km_extra > 0:
            last_km = f'''
            SELECT CONCAT(
            LPAD(EXTRACT(MINUTE FROM SEC_TO_TIME(AVG(TIME_TO_SEC(Speed)))), 2, '0'),
            ':',
            LPAD(EXTRACT(SECOND FROM SEC_TO_TIME(AVG(TIME_TO_SEC(Speed)))), 2, '0')
            ) AS average_speed
            FROM activitydata
            WHERE Distance BETWEEN {total_km * 1000} AND {total_km_result}
            ORDER BY id DESC
            LIMIT 1;
                '''

            db.connection.commit()
            db.cursor.execute(last_km)
            last_km = db.cursor.fetchone()[0]

            res_Speed.append(last_km)

            hr = f'''
            SELECT CEILING(AVG(Heart_Rate)) AS HR100 FROM activitydata
            WHERE Distance BETWEEN {total_km*1000} AND {total_km_result} ORDER BY id DESC LIMIT 1;
            '''

            db.connection.commit()
            db.cursor.execute(hr)
            hr = db.cursor.fetchone()[0]
            res_hr.append(hr)

            cd = f'''
            SELECT CEILING(AVG(Cadance)) AS cd FROM activitydata
            WHERE Distance BETWEEN {total_km*1000} AND {total_km_result} ORDER BY id DESC LIMIT 1;
            '''

            db.connection.commit()
            db.cursor.execute(cd)
            cd = db.cursor.fetchone()[0]
            res_cd.append(cd)

            al_me = f'''
            SELECT CEILING(AVG(Altitude_Meters)) AS AL_Me FROM activitydata
            WHERE Distance BETWEEN {total_km*1000} AND {total_km_result} ORDER BY id DESC LIMIT 1;
            '''

            db.connection.commit()
            db.cursor.execute(al_me)
            al_me = db.cursor.fetchone()[0]
            res_al.append(al_me)

    except mysql.connector.Error as e:
        print(f"Database error: {e.errno} - {e.msg}")
    except Exception as e:
        print(f"Other error: {e}")

    db.close_connection()

    return total_km_result, total_km