from PySide6.QtWidgets import QFrame, QGridLayout, QGraphicsDropShadowEffect
from PySide6.QtGui import QColor, QPalette

class STYLE():
    """
    PURPOSE

    Contains a library of stylesheets and functions to modify the style of the program.
    """
    # VARIABLES
    theme = True

    widgetHeight = 0

    def __init__(self):
        """
        PURPOSE

        Class constructor

        INPUT

        NONE

        RETURNS

        NONE
        """
        pass
    

    def setStylesheet(self, appObject):
        appObject.setStyleSheet(""" 
                 
            #controlPanelButton {
                font-size: 12pt;
                color: white;
                background-color: #007ACC;
                border-radius: 14px;
                padding: 6px 12px;
            }
            
            #program_exit {
                font-size: 12pt;
                color: white;
                background-color: red;
                border-radius: 14px;
                padding: 6px 12px;
            }
                                
            #dataButton, #mappingButton{
                font-size: 12pt;
                color: white;
                background-color: #424242;
                border-radius: 14px;
                padding: 6px 12px;
            }
                                
            QComboBox {
                background-color: #424242;               
            }

            QWidget {
                background-color: #161616;
                color: white;
            }  
                                
            QGroupBox {
                background-color: #212121
            }
                                
            QPushButton {
                background-color: #424242        
            }
                                
            #camera_feed_1, #camera_feed_2, #camera_feed_3, #camera_feed_4 {
                background-color: black;                    
            }
                                
            QStackedWidget, #control_panel_camera_widget, #control_panel_functions_widget, #buttonsPanel{
                border: 1px solid #fafafa;
                border-radius: 10px;
            }       
        """)
