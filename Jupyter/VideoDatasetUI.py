import ipywidgets as widgets
import numpy as np
import io
from PIL import Image
import cv2

class VideoDatasetUI:
    
    class __default_dataset:
        def video_list(): 
            return ["First", "Second", "Third"]
        def video_annotations(video_ref):
            return ["Alpha", "Beta", "Gamma"]
        def video_annotation_frame_num(video_ref, annotation_ref):
            return 35
        def video_end_frame_num(video_ref):
            return 200
        def video_start_frame_num(video_ref):
            return 21
        def video_frame(video_ref, frame_num):
            rgb_array = np.random.rand(360,640,3) * 255
            image = Image.fromarray(rgb_array.astype('uint8')).convert('RGB')
            buffer = io.BytesIO()
            image.save(buffer, format='JPEG')
            return buffer.getvalue()
        def video_annotated_frame(video_ref, annotation_ref, frame_num):
            rgb_array = np.random.rand(360,640,3) * 255
            image = Image.fromarray(rgb_array.astype('uint8')).convert('RGB')
            buffer = io.BytesIO()
            image.save(buffer, format='JPEG')
            initial_img =  buffer.getvalue()

            nparr = np.frombuffer(initial_img , np.uint8)
            im = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            im = cv2.rectangle(im, (20,30), (100,250), (255, 0, 0), 2)
            is_success, im_buf_arr = cv2.imencode(".jpg", im)
            return im_buf_arr.tobytes()


    def __init__(self, dataset = __default_dataset):
        self.__dataset = dataset
        self.__video_selected_ref = ""
    
    def display(self):
        video_list_dropdown_options = self.__dataset.video_list()
        self.__video_selected_ref = video_list_dropdown_options[0]
        
        imageArea = widgets.Image()

        video_list_dropdown = widgets.Dropdown(
            options= video_list_dropdown_options,
            value = self.__video_selected_ref,
            description='Video #:',
            disabled=False,
        )

        play = widgets.Play(
                step=1,
                interval=50,
                description="Press play",
                disabled=False
        )

        slider = widgets.IntSlider()

        widgets.jslink((play, 'value'), (slider, 'value'))

        annotations_dropdown = widgets.Dropdown(
            options= self.__dataset.video_annotations(self.__video_selected_ref),
            description='Annotated Frame #:',
            disabled=False,
        )
        
        def video_list_dropdown_value_set(): 
            annotations_dropdown.options = self.__dataset.video_annotations(self.__video_selected_ref)
            slider.min = play.min = 0
            slider.max = play.max = self.__dataset.video_end_frame_num(self.__video_selected_ref)
            slider.min = play.min = self.__dataset.video_start_frame_num(self.__video_selected_ref)
            slider.value =  slider.min

        def on_video_list_dropdown_value_change(change): 
            self.__video_selected_ref = change['new']
            video_list_dropdown_value_set()
  
        video_list_dropdown.observe(on_video_list_dropdown_value_change, names='value')

        def on_slider_value_change(change):
            print(change)
            frame_number = change['new']
            imageArea.value = self.__dataset.video_frame(self.__video_selected_ref, frame_number)
 
        slider.observe(on_slider_value_change, names='value')

        def on_annotations_dropdown_value_change(change): 
            annotation_selected_ref = change['new']
            frame_number = self.__dataset.video_annotation_frame_num(self.__video_selected_ref, annotation_selected_ref)
            play._playing = False
            slider.value = frame_number
            imageArea.value = self.__dataset.video_annotated_frame(self.__video_selected_ref, annotation_selected_ref, frame_number)
  
        annotations_dropdown.observe(on_annotations_dropdown_value_change, names='value')
        
        controls = widgets.VBox([widgets.HBox([video_list_dropdown, play, slider, annotations_dropdown]),imageArea])

        # trigger the initial video to correctly set the slider values and load the first image
        video_list_dropdown_value_set()
        on_slider_value_change({'new':0})
        return controls
