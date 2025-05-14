# app.py
import streamlit as st
import os
import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
import io
import webbrowser
from rpckit.client import Client
from models import SessionLocal, Step, Case, Action
from sqlalchemy.orm import joinedload

# Upload folder
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

VNC_PROXY = "http://10.7.60.13:8889/vnc.html?path=?token="

# Initialize RPC client and connection status in session state
if 'rpc_client' not in st.session_state:
    st.session_state.rpc_client = None
if 'connection_status' not in st.session_state:
    st.session_state.connection_status = False
if 'bbox_start' not in st.session_state:
    st.session_state.bbox_start = None
if 'bbox_end' not in st.session_state:
    st.session_state.bbox_end = None
if 'is_listening' not in st.session_state:
    st.session_state.is_listening = False
if 'machine_address' not in st.session_state:
    st.session_state.machine_address = ""

def get_db_session():
    """Create and return a new database session"""
    return SessionLocal()

def draw_bbox(image, bbox_start, bbox_end):
    """Draw bounding box on image and return the figure"""
    fig, ax = plt.subplots(1)
    ax.imshow(image)
    ax.axis('off')
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    
    # Convert bbox coordinates to float
    start_x = float(bbox_start[0])
    start_y = float(bbox_start[1])
    end_x = float(bbox_end[0])
    end_y = float(bbox_end[1])
    
    # Calculate width and height
    width = end_x - start_x
    height = end_y - start_y
    
    # Create rectangle patch
    rect = patches.Rectangle(
        (start_x, start_y), width, height,
        linewidth=2, edgecolor='r', facecolor='none'
    )
    
    # Add the patch to the Axes
    ax.add_patch(rect)
    return fig

def launch_vnc_browser(machine_address):
    """Launch browser with VNC URL in a new window"""
    try:
        # Extract IP and port
        ip, port = machine_address.split(':')
        # VNC port is typically 5900
        vnc_port = 5900
        vnc_url = f"{VNC_PROXY}{ip}:{vnc_port}"
        # Open in new window (using new=2)
        webbrowser.open_new(vnc_url)
        return True
    except Exception as e:
        st.error(f"Failed to launch VNC browser: {str(e)}")
        return False

def handle_mouse_click(event):
    """Handle mouse click events from RPC"""
    if not st.session_state.is_listening:
        return
    
    if st.session_state.bbox_start is None:
        # First click - set start point
        st.session_state.bbox_start = {"x": event['x'], "y": event['y']}
        st.info("First point set. Click again to set end point.")
    else:
        # Second click - set end point
        st.session_state.bbox_end = {"x": event['x'], "y": event['y']}
        st.session_state.is_listening = False
        st.success("Bounding box coordinates set!")

st.title("Streamlit Step Manager")

# Add tabs for different sections
tab1, tab2, tab3 = st.tabs(["Steps", "Cases", "Actions"])

with tab1:
    # Machine connection section
    st.subheader("Machine Connection")
    col1, col2 = st.columns([3, 1])
    with col1:
        machine_address = st.text_input("Machine IP:PORT", 
                                      value=st.session_state.machine_address,
                                      placeholder="e.g., 192.168.1.100:8080",
                                      key="machine_input")
    with col2:
        st.write("")  # For vertical alignment
        connect_button = st.button("Connect")

    if connect_button:
        # Disconnect existing connection if any
        if st.session_state.rpc_client is not None:
            st.session_state.rpc_client = None
            st.session_state.connection_status = False
            st.session_state.bbox_start = None
            st.session_state.bbox_end = None
            st.info("Disconnected from previous machine")
        
        if machine_address:
            try:
                # Store the machine address in session state
                st.session_state.machine_address = machine_address
                # Create RPC client connection
                st.session_state.rpc_client = Client(f"http://{machine_address}")
                # Test connection
                st.session_state.connection_status = st.session_state.rpc_client.ping()
                if st.session_state.connection_status:
                    st.success(f"Connected to {machine_address}")
                    # Launch VNC browser
                    if launch_vnc_browser(machine_address):
                        st.info("VNC browser launched")
                else:
                    st.session_state.rpc_client = None
            except Exception as e:
                st.error(f"Connection failed: {str(e)}")
                st.session_state.rpc_client = None
                st.session_state.connection_status = False
        else:
            st.error("Please enter a valid IP:PORT")

    st.subheader("Create or Update a Step")
    
    # Get all cases and actions for dropdowns
    db = get_db_session()
    try:
        cases = db.query(Case).all()
        actions = db.query(Action).all()
        
        case_options = {f"{c.id} - {c.name}": c.id for c in cases}
        action_options = {f"{a.id} - {a.name}": a.id for a in actions}
    finally:
        db.close()
    
    # Case selection first
    case_id = st.selectbox("Case", options=list(case_options.keys()))
    case_id = case_options[case_id] if case_id else None
    if not case_id:
        st.error("Please select a case")
    # Image capture and preview
    image_file = None
    if st.session_state.rpc_client is not None:
        if st.button("Capture Screenshot"):
            try:
                # Test connection before taking screenshot
                if not st.session_state.rpc_client.ping():
                    st.error("Connection lost. Please reconnect to the machine.")
                    st.session_state.rpc_client = None
                    st.session_state.connection_status = False
                
                # Call RPC method to capture screenshot
                screenshot_data = st.session_state.rpc_client.run("screenshot")
                if screenshot_data:
                    # Convert bytes to image file
                    image_file = io.BytesIO()
                    screenshot_data.save(image_file, format="PNG")
                    image_file.name = "screenshot.png"
                    st.success("Screenshot captured successfully")
                else:
                    st.error("Failed to capture screenshot: No data received")
            except Exception as e:
                raise e
                st.error(f"Failed to capture screenshot: {str(e)}")
                # Reset connection on error
                st.session_state.rpc_client = None
                st.session_state.connection_status = False
    else:
        st.warning("Please connect to a machine first to capture screenshots")
    
    # Image preview
    if image_file:
        st.subheader("Image Preview")
        # Display original image
        # st.image(image_file, caption="Original Image", width=400)
        em = st.empty()
        em.image(image_file, caption="Original Image")
        # Bbox selection using RPC mouse events
        if st.session_state.rpc_client is not None:
            st.session_state.bbox_start = None
            st.session_state.bbox_end = None
            st.info("Click two points on the VNC window to set bounding box")
            # Start listening for mouse events
            click_event = st.session_state.rpc_client.listen('mouse', 'click', 100)
            st.session_state.bbox_start = click_event.start
            st.session_state.bbox_end = click_event.end
            if st.session_state.bbox_start == st.session_state.bbox_end:
                st.sesstion_state.bbox_end = st.session_state.rpc_client.listen('mouse', 'click', 100).start
        else:
            st.error("Connection lost. Please reconnect to the machine.")

    
        # Display bbox if both points are set
        if st.session_state.bbox_start and st.session_state.bbox_end:
            # Load image for matplotlib
            image = Image.open(image_file)
            
            # Draw and display bbox
            fig = draw_bbox(image, st.session_state.bbox_start, st.session_state.bbox_end)
            em.pyplot(fig)
            plt.close(fig)
    
    # Other inputs
    number = st.number_input("Order Number", min_value=0)
    
    action_id = st.selectbox("Action", options=list(action_options.keys()))
    action_id = action_options[action_id] if action_id else None
    if not action_id:
        st.error("Please select an action")
    
    detail = st.text_input("Detail")
    thinking = st.text_input("Thinking")

    # Use bbox coordinates from RPC events if available
    bbox_start_x = st.session_state.bbox_start[0] if st.session_state.bbox_start else 0
    bbox_start_y = st.session_state.bbox_start[1] if st.session_state.bbox_start else 0
    bbox_end_x = st.session_state.bbox_end[0] if st.session_state.bbox_end else 0
    bbox_end_y = st.session_state.bbox_end[1] if st.session_state.bbox_end else 0

    action_attrs = st.text_area("Action Attributes (JSON)", value="{}")

    # Save button - disabled if case or action not selected
    save_disabled = not (case_id and action_id and image_file)
    if st.button("Save", disabled=save_disabled):
        if image_file:
            image_path = os.path.join(UPLOAD_FOLDER, image_file.name)
            with open(image_path, "wb") as f:
                f.write(image_file.read())

        db = get_db_session()
        try:
            # Create the step
            step = Step(
                case_id=case_id,
                number=number,
                image=image_path if image_file else None,
                action_id=action_id,
                detail=detail,
                thinking=thinking,
                bbox_start=json.dumps([bbox_start_x, bbox_start_y]),
                bbox_end=json.dumps([bbox_end_x, bbox_end_y]),
                action_attrs=action_attrs
            )

            # Add and commit the step
            db.add(step)
            db.commit()
            
            # Refresh the step to ensure all relationships are loaded
            db.refresh(step)
            
            # Access related objects after refresh
            case_name = step.case.name
            action_name = step.action.name
            
            st.success(f"Step saved! Case: {case_name}, Action: {action_name}")
        except Exception as e:
            db.rollback()
            st.error(f"Failed to save step: {str(e)}")
        finally:
            db.close()

    # Show existing steps
    st.subheader("Existing Steps")

    db = get_db_session()
    try:
        # Use joinedload to load relationships in a single query
        steps = db.query(Step).options(
            joinedload(Step.case),
            joinedload(Step.action)
        ).all()
    finally:
        db.close()

    for s in steps:
        st.write(f"**ID:** {s.id}")
        st.write(f"**Case:** {s.case.name} (ID: {s.case_id})")
        st.write(f"**Order:** {s.number}")
        st.write(f"**Action:** {s.action.name} (ID: {s.action_id})")
        st.write(f"**Detail:** {s.detail}")
        st.write(f"**Thinking:** {s.thinking}")
        st.write(f"**BBox Start:** {s.bbox_start}")
        st.write(f"**BBox End:** {s.bbox_end}")
        st.write(f"**Action Attrs:** {s.action_attrs}")
        if s.image:
            # Display original image
            st.image(s.image, caption="Original Image", width=200)
            
            # Display image with bbox
            image = Image.open(s.image)
            bbox_start = json.loads(s.bbox_start)
            bbox_end = json.loads(s.bbox_end)
            fig = draw_bbox(image, bbox_start, bbox_end)
            st.pyplot(fig)
            plt.close(fig)

        # Add delete button
        if st.button(f"Delete {s.id}"):
            db = get_db_session()
            try:
                step_to_delete = db.query(Step).filter(Step.id == s.id).first()
                if step_to_delete:
                    db.delete(step_to_delete)
                    db.commit()
            finally:
                db.close()
            st.experimental_rerun()

with tab2:
    st.subheader("Manage Cases")
    
    # Form to add new case
    with st.form("case_form", clear_on_submit=True):
        case_name = st.text_input("Case Name")
        case_description = st.text_area("Case Description")
        submit_case = st.form_submit_button("Add Case")
        
        if submit_case:
            db = get_db_session()
            try:
                case = Case(name=case_name, description=case_description)
                db.add(case)
                db.commit()
                st.success("Case added!")
            finally:
                db.close()
    
    # Show existing cases
    st.subheader("Existing Cases")
    db = get_db_session()
    try:
        cases = db.query(Case).all()
    finally:
        db.close()
        
    for c in cases:
        st.write(f"**ID:** {c.id}")
        st.write(f"**Name:** {c.name}")
        st.write(f"**Description:** {c.description}")
        if st.button(f"Delete Case {c.id}"):
            db = get_db_session()
            try:
                case_to_delete = db.query(Case).filter(Case.id == c.id).first()
                if case_to_delete:
                    db.delete(case_to_delete)
                    db.commit()
            finally:
                db.close()
            st.experimental_rerun()

with tab3:
    st.subheader("Manage Actions")
    
    # Form to add new action
    with st.form("action_form", clear_on_submit=True):
        action_name = st.text_input("Action Name")
        action_description = st.text_area("Action Description")
        submit_action = st.form_submit_button("Add Action")
        
        if submit_action:
            db = get_db_session()
            try:
                action = Action(name=action_name, description=action_description)
                db.add(action)
                db.commit()
                st.success("Action added!")
            finally:
                db.close()
    
    # Show existing actions
    st.subheader("Existing Actions")
    db = get_db_session()
    try:
        actions = db.query(Action).all()
    finally:
        db.close()
        
    for a in actions:
        st.write(f"**ID:** {a.id}")
        st.write(f"**Name:** {a.name}")
        st.write(f"**Description:** {a.description}")
        if st.button(f"Delete Action {a.id}"):
            db = get_db_session()
            try:
                action_to_delete = db.query(Action).filter(Action.id == a.id).first()
                if action_to_delete:
                    db.delete(action_to_delete)
                    db.commit()
            finally:
                db.close()
            st.experimental_rerun()

