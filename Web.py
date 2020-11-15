# =====================================================
#    Web.py
#      The web app for Casino
# =====================================================
from flask import Flask, render_template, url_for, flash, redirect, request, send_file
from uuid import UUID
import sys

from Utils import *
from Card import Card
from Pile import Pile
from Player import Player


# --------------------------------------------------------
# >>> import secrets
# >>> secrets.token_hex(16)
# '8bc3a7e928ccd5936aed03c4a732b0ab'
# >>>
# --------------------------------------------------------
FoliosFlask = Flask(__name__, static_url_path='/static')
FoliosFlask.config['SECRET_KEY'] = 'zSqDxzhf:JAd2hiQYXZv)vf8/a]UkX@QH9UD!DpL/evJ]DTr(v'

# --------------------------------------------------------
# Helper functions to retrieve the current game for this 
# session.
#   TODO - Move to a session, not a global variable
# --------------------------------------------------------
CurrentGame = None
def SetCurrentGame(Game):
    global CurrentGame
    CurrentGame = Game
    return CurrentGame

def GetCurrentGame():
    global CurrentGame
    return CurrentGame

# --------------------------------------------------------
# AuthCheck will be called as the first function in each
# Flask Route.  Right now, it will just return the current
# game but in the future, it could ensure that a user is 
# properly signed in too.
#    TODO - Hook up AuthCheck to an actual authentication
# --------------------------------------------------------
def AuthCheck():
    Output("AuthCheck")
    return GetCurrentGame()

# --------------------------------------------------------
# Signin
#   TODO - Implement a sign in
# --------------------------------------------------------
@FoliosFlask.route("/signin", methods=['GET', 'POST'])
def SignIn():
    Output("SignIn")
    return redirect(url_for("PlayGame"))

# --------------------------------------------------------
# SignOut
#   TODO - Implement a sign out
# --------------------------------------------------------
@FoliosFlask.route("/signout", methods=['GET', 'POST'])
def SignOut():
    Output("SignIn")
    return redirect(url_for("PlayGame"))

# --------------------------------------------------------
# PlayGame
# --------------------------------------------------------
@FoliosFlask.route("/")
@FoliosFlask.route("/playgame")
def PlayGame():
    # Auth check must come first
    #
    Game = AuthCheck()
    if not Session:
        return redirect( url_for('SignIn') )

    return render_template('dashboard.html', Session=Session, Year=Year, Item=Item, Statement=Statement, Forecast=Forecast, Charts=Charts, Models=Models)

# --------------------------------------------------------
# Home
# --------------------------------------------------------
@FoliosFlask.route("/Home")
def Home():
    return redirect(url_for('Dashboard'))

# --------------------------------------------------------
# Analysis
# --------------------------------------------------------
@FoliosFlask.route("/analysis")
def Analyze():
    # Auth check must come first
    #
    Session = AuthCheck()
    if not Session:
        return redirect( url_for('SignIn') )

    # Load in the basic financial information
    #
    Root, Parent, Item, Year = LoadItemsYear(request, Session)
    S, F, A = LoadFinancialBasics(Session, Year, Item)

    # Load the Charts
    #
    ChartBS = F.Chart("BS")
    ChartIS = F.Chart("IS")
    ChartBS.SetElementID("ChartBalanceSheet")
    ChartIS.SetElementID("ChartIncomeStatement")
    Charts = [ChartBS, ChartIS]

    # Prepare the reports which will be rendred in the HTML
    #
    Forecast = F.Report()
    Forecast.SetTitle(f"Long Term Forecast")
    ThisYear = F.Report(Year)
    ThisYear.SetTitle(f"{Year} Forecast")
    Metrics = A.Report()
    Statement = S.Report()
    Highlights = GetHighlights(F, Year)
    Models = Session.GetModels()
    ConfigReport = Item.ReportConfig()

    return render_template(
                'analysis.html', 
                Session = Session, Year = Year, Item = Item, 
                Forecast = Forecast, ThisYear = ThisYear, Statement = Statement,
                Highlights = Highlights, Config = ConfigReport, Metrics = Metrics)

# --------------------------------------------------------
# PFS
# --------------------------------------------------------
@FoliosFlask.route("/pfs", methods=['GET', 'POST'])
def PFS():
    # Auth check must come first
    #
    Session = AuthCheck()
    if not Session:
        return redirect( url_for('SignIn') )

    # Load in the basic financial information
    #
    Root, Parent, Item, Year = LoadItemsYear(request, Session)
    S, F, A = LoadFinancialBasics(Session, Year, Item)
    
    Item = Item if (Item and Item.IsFolio()) else Parent
    if not (Item and Item.IsFolio and Year):
        Output(f"PFS called on null item, non-folio item, or without a year {Year} - {Item}")
        return redirect(url_for("Dashboard"))

    # Prepare the reports which will be rendred in the HTML
    #
    PFS = Item.GetPFS(Year, Session.GetCache())
    Forecast = F.Report()

    return render_template(
                'pfs.html', 
                Session=Session, 
                Year=Year, 
                Item=Item,
                Forecast=Forecast,
                PFS=PFS,
                ReportA=PFS.GetAssetReport(),
                ReportL=PFS.GetLiabilityReport(),
                ReportI=PFS.GetIncomeReport(),
                ReportE=PFS.GetExpenseReport()
                )

# --------------------------------------------------------
# CashFlow
# --------------------------------------------------------
@FoliosFlask.route("/cashflow")
def CashFlow():
    # Auth check must come first
    #
    Session = AuthCheck()
    if not Session:
        return redirect( url_for('SignIn') )

    Root, Parent, Item, Year = LoadItemsYear(request, Session)
    Accounts = Session.GetAccounts()

    # The table of transfers
    #
    TransferList = Session.GetTransferList()
    TransferTable = []
    Header = ['Date', 'Description', 'From', 'To', 'Amount']
    TransferTable.append(Header)
    for T in TransferList:
        Row = [
            str(T.Month),
            T.Description,
            Session.FindItem(T.From).GetDisplayName(),
            Session.FindItem(T.To).GetDisplayName(),
            FloatToCurrencyShort(T.Amount)
        ]
        TransferTable.append(Row)

    # Some account reports
    #
    AccountReports = []
    AccountReports.append(CombinedAccountReport(Session, Session.GetAccounts(), 2020))
    AccountReports.append(CombinedAccountReport(Session, Session.GetAccounts(), 2021))
    AccountReports.append(CombinedAccountReport(Session, Session.GetAccounts(), 2022))
    
    # Some plans for different years
    #
    Transfers = Session.GetTransfers()
    Plans = []
    RootPlan = Root.GetPlan("", Session.GetCache())
    Plans.append(RootPlan.Report(Transfers, 2020))
    Plans.append(RootPlan.Report(Transfers, 2021))
    Plans.append(RootPlan.Report(Transfers, 2022))

    return render_template(
                'cashflow.html', 
                Session = Session,
                Accounts = Accounts,
                TransferTable = TransferTable,
                AccountReports = AccountReports,
                Plans = Plans)

# --------------------------------------------------------
# CashFlow
# --------------------------------------------------------
@FoliosFlask.route("/timeline")
def TimeLine():
    # Auth check must come first
    #
    Session = AuthCheck()
    if not Session:
        return redirect( url_for('SignIn') )

    Root, Parent, Item, Year = LoadItemsYear(request, Session)
    Transfers = Session.GetTransfers()
    RootPlan = Root.GetPlan("", Session.GetCache())
    ThisYear = RootPlan.Report(Transfers, Year)
    ThisYear.SetTitle(f"{Year} Timeline")
    Years = RootPlan.GetYears()
    Output(Years)

    return render_template('timeline.html', Session = Session, ThisYear = ThisYear, Years = Years)

# ----------------------------------------------------------------
# Show the form for any type of Financial Item and process the submission
# ----------------------------------------------------------------
def ItemForm(Session, ItemType, Item, Form, URL, Title, CreateMode):
    # HTTP POST Processing
    #
    if Form.validate_on_submit():
        Output('Form validated')
        if not Form.Submit.data:                        # Cancel was pressed
            return redirect(url_for('Dashboard'))    
        if CreateMode is True:                          # A submission from a creation action
            Output(F"Add an item - {Item}, - {Form.GetCreateScript()}")        
            Controller = GetController()
            for Line in Form.GetCreateScript():
                Cmd = Controller.ParseScriptLine(Line)
                if Cmd:
                    Controller.Execute(Cmd)
        else:                                           # A submission from an edit action
            Config = Item.GetConfig()
            Output(f'Updating configuration, orig: {Config}')
            Form.populate_obj(Config)
            Config.Add("SubType", Form.GetSelectedSubType())
            Output(f'Updating configuration, new:  {Config}')
            Item.ImportConfig(Config)
            Output(F"Item edited - {Item}")
            Session.Dirty()
        return redirect(url_for('Dashboard'))
    else:                                               # An error
        Output(f'{ItemType} form did not validate: {Form.errors}')
    
    Actuals = Contributions = Draws = None
    if not CreateMode:
        Actuals = Report(f"Recorded values for {Item.GetDisplayName()}", 2)
        Actuals.FromDict(Item.Actuals, "Date", "Recorded value", FloatToCurrencyShort)
        Contributions = Report(f"Contributions for {Item.GetDisplayName()}", 2)
        Contributions.FromDict(Item.Contributions, "Date", "Contribution", FloatToCurrencyShort, 1)
        Draws = Report(f"Contributions for {Item.GetDisplayName()}", 2)
        Draws.FromDict(Item.Contributions, "Date", "Draw", FloatToCurrencyShort, -1)

    SubTypes = None
    if ItemType != 'Folio':
        SubTypes = Form.GetModes()

    # HTTP GET Processing
    #
    return render_template(
        URL, 
        Session = Session,
        ItemType = ItemType,
        SubTypes = SubTypes,
        Item = Item,
        Form = Form,
        Title = Title, 
        Actuals = Actuals,
        Contributions = Contributions,
        Draws = Draws,
        CreateMode = CreateMode)

ClassMap = {
    'Folio': [Folio, FolioForm],
    'Asset': [Asset, AssetForm],
    'Liability': [Liability, LiabilityForm],
    'IncomeStream': [IncomeStream, IncomeStreamForm],
    'ExpenseStream': [ExpenseStream, ExpenseStreamForm]
}

def GetDefaultSettings(Class, Parent):
    Object = Class()
    Config = Object.GetConfig()
    #Output(f"XXX - {Config}")
    Config.Set('Start', DateToInputStr(Parent.GetStart()))
    Config.Set('End', DateToInputStr(Parent.GetEnd()))
    return Config

# --------------------------------------------------------
# Create Item Route
# --------------------------------------------------------
@FoliosFlask.route("/create", methods=['GET', 'POST'])
def Create():
    # Auth check must come first
    #
    Session = AuthCheck()
    if not Session:
        return redirect( url_for('SignIn') )

    Root, Parent, Item, Year = LoadItemsYear(request, Session)
    ItemType = request.args.get('ItemType', None)         # ItemType = Asset, Liability, etc. 
    SubType = request.args.get('SubType', None)          # SubType = CreditLine, Stocks, etc.

    if ItemType is None or ItemType not in ClassMap:
        return render_template('comingsoon.html', title='Coming soon...', Session=GetController().GetSession(), Form=None)
    Params = ClassMap[ItemType]
    Class = Params[0]
    FormType = Params[1]
    Output(f'{Class} - {FormType}')

    ItemTitle = ItemType if ItemType != 'Folio' else 'Folder'
    Title = FormatSettingsName(ItemTitle)
    Settings = GetDefaultSettings(Class, Session.GetCurrentFolio())
    Form = FormType(request.form, obj=Settings)
    Form.Init()
    Form.CreateMode(SubType)

    return ItemForm(Session, ItemType, None, Form, 'item.html', Title, True)

# --------------------------------------------------------
# Edit Route
# --------------------------------------------------------
@FoliosFlask.route("/edit", methods=['GET', 'POST'])
def Edit(UID = None):
    # Auth check must come first
    #
    Session = AuthCheck()
    if not Session:
        return redirect( url_for('SignIn') )

    Root, Parent, Item, Year = LoadItemsYear(request, Session)
    SubType = request.args.get('SubType', None)         # ItemType = Asset, Liability, etc.  SubType = CreditLine, Stocks, etc.

    ItemType = Item.GetClassName()
    SubType = SubType if SubType else Item.GetSetting("SubType")
    Params = ClassMap[ItemType]
    Class = Params[0]
    FormType = Params[1]

    URL = 'item.html'
    ItemTitle = ItemType if ItemType != 'Folio' else 'Folder'
    Title = "Edit " + ItemTitle
    Settings = Item.GetConfig()
    Output(f"Edit Item: {Item}")
    Output(f"   Settings: {Settings}")

    Form = FormType(request.form, obj=Settings)
    Form.Init()
    Form.EditMode(SubType)

    return ItemForm(Session, ItemType, Item, Form, URL, Title, False)

def NvpForm(Session, Item, Form, URL, Title, Type):
    # HTTP POST Processing
    #
    if Form.validate_on_submit():
        Output('Form validated')
        if not Form.Submit.data:                        # Cancel was pressed
            return redirect(url_for('Dashboard'))    
        else:                                           # A name value pair was submitted
            Config = ItemConfig()
            Form.populate_obj(Config)
            Output(f'Name value pair:  {Config}')
            if Type == "Actuals":
                Item.Record(DateFromString(str(Config.GetValue('Date'))), float(Config.GetValue('Value')))
                Output(f"Updated the acutals for {Item}")
                Session.Dirty() 
                return redirect(url_for('Edit', ID=Item.GetID()))
            elif Type == "Contribution":
                Item.Contribute(DateFromString(str(Config.GetValue('Date'))), float(Config.GetValue('Value')))
                Output(f"Recorded a contribution for {Item}")
                Session.Dirty() 
                return redirect(url_for('Edit', ID=Item.GetID()))
        return redirect(url_for('Home'))
    else:                                               # An error
        Output(f'{Type} form did not validate: {Form.errors}')

    # HTTP GET Processing
    #
    return render_template(
        URL, 
        Title = Title, 
        Session = Session, 
        Form = Form, 
        Item = Item, 
        Type = Type)    

# --------------------------------------------------------
# Record Route
# --------------------------------------------------------
@FoliosFlask.route("/record", methods=['GET', 'POST'])
def Record(UID = None):
    # Auth check must come first
    #
    Session = AuthCheck()
    if not Session:
        return redirect( url_for('SignIn') )

    Root, Parent, Item, Year = LoadItemsYear(request, Session)
    Type = request.args.get('Type', None)

    RecordMap = {}
    RecordMap["Actuals"] = ActualsForm
    RecordMap["Contribution"] = ContributionsForm

    if not Item or not Type or Type not in RecordMap:
        Output("Record - ID is None")
        return render_template('ComingSoon.html', title='Coming Soon...', Session=Session, Form=FinancialItemForm())

    FormType = RecordMap[Type]
    URL = 'nvp.html'
    Title = Type
    Config = ItemConfig()
    Config.Add('Date', Date.Today())
    Config.Add('Value', 0.0)
    Form = FormType(request.form, obj=Config)
    Form.Init()

    return NvpForm(Session, Item, Form, URL, Title, Type)

# --------------------------------------------------------
# Record Route
# --------------------------------------------------------
@FoliosFlask.route("/transfer", methods=['GET', 'POST'])
def CreateTransfer():
    # Auth check must come first
    #
    Session = AuthCheck()
    if not Session:
        return redirect( url_for('SignIn') )

    # Setup 
    #
    URL = 'transfer.html'
    Title = 'Record a new Transfer'
    Config = ItemConfig()
    Config.Add('Date', Date.Today())
    Form = TransferForm(request.form, obj=Config)
    Form.Init()

    # HTTP POST Processing
    #
    if Form.validate_on_submit():
        Output('Transfer form validated')
        if not Form.Submit.data:                        # Cancel was pressed
            return redirect(url_for('Dashboard'))    
        else:                                           # A transfer was submitted
            Config = ItemConfig()
            Form.populate_obj(Config)
            Output(f'New transfer request: {Config}')
            FromName = str(Config.GetValue("From"))
            ToName = str(Config.GetValue("To"))
            From = Session.FindChild(FromName)
            To = Session.FindChild(ToName)
            Output(f"From: {From.GetName()} to {To.GetName()}")
            if To and From:
                Month = DateFromString(str(Config.GetValue("Date")))
                Amount = float(Config.GetValue("Amount"))
                Description = str(Config.GetValue("Description"))
                T = Transfer(Month, From.GetID(), From.GetName(), To.GetID(), To.GetName(), Amount, Description)
                Session.AddTransfer(T)
                Output(f"New transfers was recorded")
                Session.Dirty() 
            else:
                Output(f"Unable to find To and from for a new transfer: {To} |||| {From}")
        return redirect(url_for('CashFlow'))
    else:                                               # An error
        Output(f'TransferForm form did not validate: {Form.errors}')

    # HTTP GET Processing
    #
    return render_template(URL, Title = Title, Session = Session, Form = Form)    

# --------------------------------------------------------
# Save 
# --------------------------------------------------------
@FoliosFlask.route("/save", methods=['GET', 'POST'])
def Save():
    # Auth check must come first
    #
    Session = AuthCheck()
    if not Session:
        return redirect( url_for('SignIn') )

    Output("Saving")
    Model = request.args.get('Model', None)
    Session.Save(True, Model + ".mp")
    return redirect(url_for("Dashboard"))

# --------------------------------------------------------
# Save New
# --------------------------------------------------------
@FoliosFlask.route("/savenew", methods=['GET', 'POST'])
def SaveNew():
    # Auth check must come first
    #
    Session = AuthCheck()
    if not Session:
        return redirect( url_for('SignIn') )

    Output("Saving New")
    Config = ItemConfig()
    Config.Add('Save', '')
    Form = SaveForm(request.form, obj=Config)
    Form.Init()

    if Form.validate_on_submit():
        Output('Received a POST from the SaveForm')
        if not Form.Save.data:                        # Cancel was pressed
            return redirect(url_for('Dashboard'))    
        Config = ItemConfig()
        Form.populate_obj(Config)
        Output(f'Save new model request: {Config}')
        Model = Config.GetValue("Model")
        if Model:
            Model = str(Model)
            Output(f"Model file name: {Model}")
            Session.Save(True, Model + ".mp")
            return redirect(url_for("Dashboard"))

    return render_template("save.html", Session = Session, Form = Form, Title = "Save a new model")

# --------------------------------------------------------
# Delete Model 
# --------------------------------------------------------
@FoliosFlask.route("/deletemodel", methods=['GET', 'POST'])
def DeleteModel():
    # Auth check must come first
    #
    Session = AuthCheck()
    if not Session:
        return redirect( url_for('SignIn') )

    Output("Deleting model")
    Model = request.args.get('Model', None)
    Session.DeleteModel(Model + ".mp")
    return redirect(url_for("ManageModels"))

# --------------------------------------------------------
# Manage Models 
# --------------------------------------------------------
@FoliosFlask.route("/managemodels", methods=['GET', 'POST'])
def ManageModels():
    # Auth check must come first
    #
    Session = AuthCheck()
    if not Session:
        return redirect( url_for('SignIn') )

    Output("Managing model")
    Models = Session.GetModels()
    return render_template("managemodels.html", Session = Session, Title = "Available models", Models = Models)

# --------------------------------------------------------
# Load 
# --------------------------------------------------------
@FoliosFlask.route("/load", methods=['GET', 'POST'])
def Load():
    # Auth check must come first
    #
    Session = AuthCheck()
    if not Session:
        return redirect( url_for('SignIn') )

    Output("Loading")
    Model = request.args.get('Model', None)
    if Model:
        Session.Reset()
        Session.Load(True, Model + ".mp", Controller)
    return redirect(url_for("Dashboard"))

# --------------------------------------------------------
# Reset 
# --------------------------------------------------------
@FoliosFlask.route("/reset", methods=['GET', 'POST'])
def Reset():
    # Auth check must come first
    #
    Session = AuthCheck()
    if not Session:
        return redirect( url_for('SignIn') )

    Output("Reset")
    Session.Reset()
    return redirect(url_for("Dashboard"))

# --------------------------------------------------------
# Move 
# --------------------------------------------------------
@FoliosFlask.route("/move", methods=['GET', 'POST'])
def Move():
    # Auth check must come first
    #
    Session = AuthCheck()
    if not Session:
        return redirect( url_for('SignIn') )

    Root, Parent, Item = LoadItems(request, Session)
    Folios = Root.CollectFolios()

    if not (Item and Parent):
        Output(f"Move: error, either Item or Parent is null Item = {Item} ||| Parent = {Parent}")
        return redirect(url_for("Dashboard"))

    Output(f"Moving... Item = {Item.GetDisplayName()}, Parent = {Parent.GetDisplayName()}")
    return render_template("move.html", Session = Session, Item = Item, Parent = Parent, Folios = Folios)

# --------------------------------------------------------
# Move Commit
# --------------------------------------------------------
@FoliosFlask.route("/movecommit", methods=['GET', 'POST'])
def MoveCommit():
    # Auth check must come first
    #
    Session = AuthCheck()
    if not Session:
        return redirect( url_for('SignIn') )

    Root, OldParent, Item = LoadItems(request, Session)
    NewParentID = request.args.get('NewParentID', None)
    NewParent = Session.FindItem(NewParentID)

    if Item and OldParent and NewParent:
        OldParent.PullItem(Item)
        NewParent.AddItem(Item)
        Output(f"{Item.GetDisplayName()} has been moved from {OldParent.GetDisplayName()} to {NewParent.GetDisplayName()}")
        Session.Dirty()
    else:
        Output(f"MoveCommit failed ||| {Item} ||| {OldParent} ||| {NewParent}")

    return redirect(url_for("Dashboard"))

# --------------------------------------------------------
# Delete 
# --------------------------------------------------------
@FoliosFlask.route("/delete", methods=['GET', 'POST'])
def Delete():
    # Auth check must come first
    #
    Session = AuthCheck()
    if not Session:
        return redirect( url_for('SignIn') )

    Root, Parent, Item = LoadItems(request, Session)
    RecordMonth = request.args.get('Record', None)
    ContributionMonth = request.args.get('Contribution', None)

    if RecordMonth:
        RecordMonth = DateFromString(RecordMonth)
        Output(f"Deleting record for {Item.GetDisplayName()} on {RecordMonth}")
        Item.DeleteRecord(RecordMonth)
        Session.Dirty()
        return redirect(url_for("Edit", ID=Item.GetID()))
    elif ContributionMonth:
        ContributionMonth = DateFromString(ContributionMonth)
        Output(f"Deleting contribution for {Item.GetDisplayName()} on {ContributionMonth}")
        Item.DeleteContribution(ContributionMonth)
        Session.Dirty()
        return redirect(url_for("Edit", ID=Item.GetID()))
    else:
        if Item:
            Output(f"Deleting {Item.GetID()}")
            Session.DeleteItem(Item.GetID())
        else:
            Output(f'Cannot find item to delete, parent={Parent}')


    return redirect(url_for("Dashboard", ID=Session.GetCurrentItem().GetID()))

# --------------------------------------------------------
# Download
# --------------------------------------------------------
@FoliosFlask.route("/downloadv2", methods=['GET'])
def Download():
    # Auth check must come first
    #
    Session = AuthCheck()
    if not Session:
        return redirect( url_for('SignIn') )

    Output("Download()")
    FileName = Session.SaveForDownload()
    return send_file(FileName, as_attachment=True, cache_timeout=-1)

# --------------------------------------------------------
# If we were invoked directly from the command line, just 
# run flask for the app
# --------------------------------------------------------
if __name__ == "__main__":
    ScriptFile = 'MoneyPredicted.mp'
    if len(sys.argv) > 1:
        ScriptFile = sys.argv[1]

    Session = Session()
    Controller = SetController(FolioController())
    Controller.SetSession(Session)
    #LoadConfiguration(Controller, ScriptFile)
    FoliosFlask.run(debug=True, host='0.0.0.0')
