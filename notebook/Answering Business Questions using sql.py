#!/usr/bin/env python
# coding: utf-8

# # Answering Business Questions using SQL|

# ## Conectando com o SQL

# In[11]:


get_ipython().run_cell_magic('capture', '', '%load_ext sql\n%sql sqlite:///chinook.db')


# ## Analisando DB

# In[12]:


get_ipython().run_cell_magic('sql', '', 'SELECT\n    name,\n    type\nFROM sqlite_master\nWHERE type IN ("table","view");')


# In[15]:


get_ipython().run_cell_magic('sql', '', '\nSELECT * FROM genre LIMIT 5')


# In[16]:


get_ipython().run_cell_magic('sql', '', '\nSELECT * FROM customer LIMIT 5')


# ## Total de vendas por gênero - USA

# In[104]:


get_ipython().run_cell_magic('sql', '', "\nWITH\n    usa AS\n        (\n        SELECT *\n        FROM customer\n        WHERE country = 'USA'\n        ),\n    genre_total AS\n        (\n        SELECT\n            inv.invoice_id,\n            inv.customer_id,\n            g.name genre_name,\n            inv.total total_purchased\n        FROM invoice inv\n        INNER JOIN invoice_line invl ON inv.invoice_id = invl.invoice_line_id\n        INNER JOIN track t ON invl.invoice_line_id = t.track_id\n        LEFT JOIN genre g ON t.genre_id = g.genre_id\n        ),\n    consolidated AS\n        (\n        SELECT SUM(total) total_consolidated FROM invoice\n        )\n\nSELECT \n    gt.genre_name, \n    ROUND(CAST(SUM(gt.total_purchased) AS FLOAT), 3) total_purchased,\n    ROUND(CAST(SUM(gt.total_purchased) AS FLOAT)/\n        (\n            SELECT SUM(total) total_consolidated FROM invoice\n        ), 5) percent,\n    usa.country\nFROM genre_total gt\nINNER JOIN usa ON gt.customer_id = usa.customer_id\nGROUP BY 1\nORDER BY 3 DESC;")


# É possível observar  que Rock e Latin são os gêneros mais consumidos pelo país. Ironicamente o Rock And Roll é o último da lista.

# ## Total vendido por Agente 

# In[67]:


get_ipython().run_cell_magic('sql', '', 'SELECT * FROM employee WHERE title = "Sales Support Agent";')


# In[77]:


get_ipython().run_cell_magic('sql', '', "\nWITH\n    total_cliente AS\n        (\n        SELECT \n            c.customer_id,\n            c.support_rep_id,\n            SUM(inv.total) total_sales\n        FROM customer c\n        INNER JOIN invoice inv ON c.customer_id = inv.customer_id\n        GROUP BY 2\n        )\n        \nSELECT \n    e.first_name || ' ' || e.last_name salesman,\n    ROUND(tc.total_sales, 0)\nFROM total_cliente tc\nINNER JOIN employee e ON tc.support_rep_id = employee_id\nORDER BY 2 DESC;")


# É possível observar que Jane é a melhor vendedora , seguida por Margaret e Steve respectivamente. A diferença entre as vendas dos três é relativamente próxima. 

# ## Analisando clientes por países

# In[150]:


get_ipython().run_cell_magic('sql', '', 'DROP VIEW customer_country;')


# In[151]:


get_ipython().run_cell_magic('sql', '', '\nCREATE VIEW customer_country AS\n    SELECT \n        COUNT(c.customer_id) AS customer_count,\n        ROUND(inv.total_purchased, 0) AS total_purchased, \n        c.country\n    FROM customer c\n    INNER JOIN (\n                SELECT \n                    customer_id,\n                    SUM(total) total_purchased\n                FROM invoice\n                GROUP BY 1) inv ON c.customer_id = inv.customer_id\n    GROUP BY 3;\n\n\nSELECT * FROM customer_country LIMIT 5;')


# In[172]:


get_ipython().run_cell_magic('sql', '', '\nDROP VIEW customer_country_analisys;')


# In[173]:


get_ipython().run_cell_magic('sql', '', '\nCREATE VIEW customer_country_analisys AS\n    SELECT\n        SUM(cc.customer_count) total_customers,\n        SUM(cc.total_purchased) total_purchased,\n    ROUND(cc.total_purchased/cc.customer_count, 0) sales_per_customer,\n    CASE\n        WHEN cc.customer_count = 1 THEN "Other"\n        ELSE cc.country END \'country\'\n    FROM customer_country cc\n    GROUP BY 4\n    ORDER BY 3 DESC;\n\nSELECT * FROM customer_country_analisys;')


# É possível observar que os clientes dos países que tem apenas um cliente ('Other') tem um consumo acima da média e movimentam boa parte do lucro total. 

# In[181]:


get_ipython().run_cell_magic('sql', '', '\nSELECT \nROUND(AVG(total_purchased), 4) AS avg_total_purchased,\nROUND(AVG(sales_per_customer), 4) AS avg_sales_per_customer\nFROM customer_country_analisys;')


# In[159]:


get_ipython().run_cell_magic('sql', '', '\nSELECT country, customer_count \nFROM customer_country\nWHERE customer_count = 1;')


# Também conseguimos observar que:
#     - O país que mais consome individualmente é a Czech Republic
#     - O país que menos consome no valor absoluto é a India
#     - O país com o menor consumo por cliente é os USA. 

# In[184]:


## Comparing albuns with individual tracks|


# In[185]:


get_ipython().run_cell_magic('sql', '', '\nWITH invoice_first_track AS\n    (\n     SELECT\n         il.invoice_id invoice_id,\n         MIN(il.track_id) first_track_id\n     FROM invoice_line il\n     GROUP BY 1\n    )\n\nSELECT\n    album_purchase,\n    COUNT(invoice_id) number_of_invoices,\n    CAST(count(invoice_id) AS FLOAT) / (\n                                         SELECT COUNT(*) FROM invoice\n                                      ) percent\nFROM\n    (\n    SELECT\n        ifs.*,\n        CASE\n            WHEN\n                 (\n                  SELECT t.track_id FROM track t\n                  WHERE t.album_id = (\n                                      SELECT t2.album_id FROM track t2\n                                      WHERE t2.track_id = ifs.first_track_id\n                                     ) \n\n                  EXCEPT \n\n                  SELECT il2.track_id FROM invoice_line il2\n                  WHERE il2.invoice_id = ifs.invoice_id\n                 ) IS NULL\n             AND\n                 (\n                  SELECT il2.track_id FROM invoice_line il2\n                  WHERE il2.invoice_id = ifs.invoice_id\n\n                  EXCEPT \n\n                  SELECT t.track_id FROM track t\n                  WHERE t.album_id = (\n                                      SELECT t2.album_id FROM track t2\n                                      WHERE t2.track_id = ifs.first_track_id\n                                     ) \n                 ) IS NULL\n             THEN "yes"\n             ELSE "no"\n         END AS "album_purchase"\n     FROM invoice_first_track ifs\n    )\nGROUP BY album_purchase;')


# In[ ]:




